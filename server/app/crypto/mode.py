import secrets
from typing import Tuple


# GF(2^128) defined by 1 + a + a^2 + a^7 + a^128
# 0xE1000000000000000000000000000000: 1 + a + a^2 + a^7
# Please note the MSB is x0 and LSB is x127
def gf_2_128_mul(x, y):
    assert x < (1 << 128)
    assert y < (1 << 128)
    res = 0
    for i in range(127, -1, -1):
        res ^= x * ((y >> i) & 1)  # branchless
        x = (x >> 1) ^ ((x & 1) * 0xE1000000000000000000000000000000)
    assert res < 1 << 128
    return res


class Counter(object):
    """
    A counter object for CTR mode that combines a 12-byte nonce with a 4-byte counter.

    The full counter is 16 bytes: [nonce (12 bytes)] || [counter (4 bytes)]
    """

    def __init__(self, nonce: bytes, initial_value: int = 1):
        """
        Initialize the counter.

        :param nonce: A 12-byte value that must be unique for each encryption operation.
        :param initial_value: A 32-bit integer for the counter part (default is 1).
        """
        if len(nonce) != 12:
            raise ValueError("Nonce must be exactly 12 bytes.")
        if not (0 <= initial_value < (1 << 32)):
            raise ValueError(
                "Initial counter value must be a 32-bit integer (0 <= value < 2^32)."
            )

        # Store nonce as a list of integers (bytes)
        self._nonce = list(nonce)
        # Convert the initial counter to a 4-byte big-endian list of integers.
        self._counter_part = list(initial_value.to_bytes(4, byteorder="big"))
        # The complete counter is the nonce concatenated with the counter part.
        self._counter = self._nonce + self._counter_part

    @property
    def value(self) -> bytes:
        """
        Return the current 16-byte counter block as bytes.
        """
        return bytes(self._counter)

    def increment(self):
        """
        Increment the counter portion (the last 4 bytes) by one.
        If the counter portion overflows, it wraps around to zero.
        """
        # We increment only the last 4 bytes (indexes 12 to 15)
        for i in range(15, 11, -1):
            self._counter[i] += 1
            if self._counter[i] < 256:
                break
            # Carry over: set current byte to 0 and continue with the next.
            self._counter[i] = 0
        # Note: When the 4-byte counter overflows, it wraps around.


class BlockCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, plaintext: bytes) -> bytes: ...

    def decrypt(self, ciphertext: bytes) -> bytes: ...


class CTRMode:
    def __init__(self, block_cipher: BlockCipher, counter: Counter | None = None):
        self._block_cipher = block_cipher

        if counter is None:
            nonce = secrets.token_bytes(12)
            counter = Counter(nonce, 2)

        self._counter = counter
        self._remaining_counter = []

    def encrypt(self, plaintext: bytes) -> bytes:
        while len(self._remaining_counter) < len(plaintext):
            self._remaining_counter += self._block_cipher.encrypt(self._counter.value)
            self._counter.increment()

        encrypted = [(p ^ c) for (p, c) in zip(plaintext, self._remaining_counter)]
        # Remove the bytes we used, so we don't use them again. We still keep the
        # remaining counter for the next call, so we don't need to generate a new
        # block every time.
        self._remaining_counter = self._remaining_counter[len(encrypted) :]

        return bytes(encrypted)

    def decrypt(self, ciphertext: bytes) -> bytes:
        # AES-CTR is symetric
        return self.encrypt(ciphertext)


class GCMMode:
    def __init__(
        self, aes_cipher, nonce: bytes | None = None, associated_data: bytes = b""
    ):
        """
        aes_cipher: Your AES block cipher instance (must have an encrypt(block) method).
        nonce: Optional 12-byte nonce; if None, a random 12-byte nonce is generated.
        associated_data: Additional authenticated data (AAD) as bytes.
        """
        self.aes_cipher = aes_cipher
        self.AAD = associated_data

        if nonce is None:
            nonce = secrets.token_bytes(12)
        if len(nonce) != 12:
            raise ValueError("Nonce must be 12 bytes for GCM mode.")
        self.nonce = nonce

        counter = Counter(self.nonce, 1)
        self.Y0 = counter.value
        counter.increment()

        # Compute hash subkey H = E(K, 0^128)
        H_block = self.aes_cipher.encrypt(b"\x00" * 16)
        self.H_int = int.from_bytes(H_block, byteorder="big")

        # Initialize your CTR mode with the underlying AES cipher.
        # We assume your CTR mode class (e.g., cipher_mode.CTRMode) allows resetting its counter.
        self.ctr = CTRMode(self.aes_cipher, counter)

    def _compute_ghash(self, A: bytes, C: bytes) -> bytes:
        """
        Compute GHASH over the AAD (A) and ciphertext (C).
        """

        def pad(data: bytes) -> bytes:
            if len(data) % 16 == 0:
                return data
            return data + b"\x00" * (16 - len(data) % 16)

        X = 0
        # Process padded AAD and ciphertext.
        for data in (pad(A), pad(C)):
            for i in range(0, len(data), 16):
                block = data[i : i + 16]
                block_int = int.from_bytes(block, byteorder="big")
                X = gf_2_128_mul(X ^ block_int, self.H_int)
        # Process lengths (in bits) of AAD and ciphertext.
        a_len = len(A) * 8
        c_len = len(C) * 8
        len_block = a_len.to_bytes(8, byteorder="big") + c_len.to_bytes(
            8, byteorder="big"
        )
        X = gf_2_128_mul(X ^ int.from_bytes(len_block, byteorder="big"), self.H_int)
        return X.to_bytes(16, byteorder="big")

    def encrypt(self, plaintext: bytes) -> Tuple[bytes, bytes]:
        """
        Encrypt plaintext and compute the authentication tag.
        Returns a tuple (ciphertext, tag).
        """
        # Compute tag: tag = E(K, Y₀) XOR S.
        E_Y0 = self.aes_cipher.encrypt(self.Y0)

        # Use your CTR mode to encrypt the plaintext.
        ciphertext = self.ctr.encrypt(plaintext)

        # Compute GHASH over AAD and ciphertext.
        S = self._compute_ghash(self.AAD, ciphertext)

        tag_int = int.from_bytes(E_Y0, byteorder="big") ^ int.from_bytes(
            S, byteorder="big"
        )
        tag = tag_int.to_bytes(16, byteorder="big")
        return ciphertext, tag

    def decrypt(self, ciphertext: bytes, tag: bytes) -> bytes:
        """
        Verify the authentication tag and decrypt the ciphertext.
        Raises an error if tag verification fails.
        """
        # Compute expected tag.
        S = self._compute_ghash(self.AAD, ciphertext)
        E_Y0 = self.aes_cipher.encrypt(self.Y0)
        expected_tag_int = int.from_bytes(E_Y0, byteorder="big") ^ int.from_bytes(
            S, byteorder="big"
        )
        expected_tag = expected_tag_int.to_bytes(16, byteorder="big")
        if expected_tag != tag:
            raise ValueError("Authentication tag mismatch!")
        # Decrypt using CTR mode.
        plaintext = self.ctr.decrypt(ciphertext)
        return plaintext
