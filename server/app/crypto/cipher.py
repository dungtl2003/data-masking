"""
AES Block Cipher.

Performs single block cipher decipher operations on a 16 element list of integers.
These integers represent 8 bit bytes in a 128 bit block.
The result of cipher or decipher operations is the transformed 16 element list of integers.

Algorithm per NIST FIPS-197 http://csrc.nist.gov/publications/fips/fips197/fips-197.pdf
"""

# Normally use relative import. In test mode use local import.
from app.crypto.mode import BlockCipher
from app.crypto.aes.key_expander import KeyExpander
from app.crypto.aes import aes_tables


class AESCipher:
    """Perform single block AES cipher/decipher"""

    def __init__(self, expanded_key):
        # Store epanded key
        self._expanded_key = expanded_key

        # Number of rounds determined by expanded key length
        self._Nr = int(len(expanded_key) / 16) - 1

    def _sub_bytes(self, state):
        """
        Run state through sbox
        """
        for i, s in enumerate(state):
            state[i] = aes_tables.sbox[s]

    def _i_sub_bytes(self, state):
        """
        Run state through inverse sbox
        """
        for i, s in enumerate(state):
            state[i] = aes_tables.i_sbox[s]

    def _shift_row(self, row, shift):
        """
        Circular shift row left by shift amount
        """
        row += row[:shift]
        del row[:shift]
        return row

    def _i_shift_row(self, row, shift):
        """
        Circular shift row right by shift amount
        """
        row += row[:shift]
        del row[: 4 + shift]
        return row

    def _shift_rows(self, state):
        """
        Shift rows of state
        """
        for i in 1, 2, 3:
            state[i::4] = self._shift_row(state[i::4], i)

    def _i_shift_rows(self, state):
        # Extract rows as every 4th item starting at [1..3]
        # Replace row with inverse shift_row operation
        for i in 1, 2, 3:
            state[i::4] = self._i_shift_row(state[i::4], -i)

    def _mix_column(self, column, inverse):
        # Use galois lookup tables instead of performing complicated operations
        # If inverse, use matrix with inverse values
        g0, g1, g2, g3 = aes_tables.galI if inverse else aes_tables.galNI
        c0, c1, c2, c3 = column
        return (
            g0[c0] ^ g1[c1] ^ g2[c2] ^ g3[c3],
            g3[c0] ^ g0[c1] ^ g1[c2] ^ g2[c3],
            g2[c0] ^ g3[c1] ^ g0[c2] ^ g1[c3],
            g1[c0] ^ g2[c1] ^ g3[c2] ^ g0[c3],
        )

    def _mix_columns(self, state, inverse):
        # Perform mix_column for each column in the state
        for i, j in (0, 4), (4, 8), (8, 12), (12, 16):
            state[i:j] = self._mix_column(state[i:j], inverse)

    def _add_round_key(self, state, round):
        # XOR the state with the current round key
        for k, (i, j) in enumerate(
            zip(state, self._expanded_key[round * 16 : (round + 1) * 16])
        ):
            state[k] = i ^ j

    def cipher_block(self, state: list) -> list:
        """Perform AES block cipher on input"""
        # state is a flat list of 16 bytes ([b0, b1, b2, ... b15], [b0, b1, b2, b3] is a column)

        # PKCS7 Padding
        state = state + [16 - len(state)] * (
            16 - len(state)
        )  # Fails test if it changes the input with +=

        self._add_round_key(state, 0)

        for i in range(1, self._Nr):
            self._sub_bytes(state)
            self._shift_rows(state)
            self._mix_columns(state, False)
            self._add_round_key(state, i)

        self._sub_bytes(state)
        self._shift_rows(state)
        self._add_round_key(state, self._Nr)
        return state

    def decipher_block(self, state):
        """Perform AES block decipher on input"""
        # null padding. Padding actually should not be needed here with valid input.
        state = state + [0] * (16 - len(state))

        self._add_round_key(state, self._Nr)

        for i in range(self._Nr - 1, 0, -1):
            self._i_shift_rows(state)
            self._i_sub_bytes(state)
            self._add_round_key(state, i)
            self._mix_columns(state, True)

        self._i_shift_rows(state)
        self._i_sub_bytes(state)
        self._add_round_key(state, 0)
        return state


class AES(BlockCipher):
    def __init__(self, key: bytes):
        key_expander = None
        if len(key) == 16:
            key_expander = KeyExpander(128)
        elif len(key) == 24:
            key_expander = KeyExpander(192)
        elif len(key) == 32:
            key_expander = KeyExpander(256)
        else:
            raise ValueError("Invalid key size")

        expanded_key = key_expander.expand(key)
        self._cipher = AESCipher(expanded_key)

    def encrypt(self, plaintext: bytes) -> bytes:
        state = list(bytearray(plaintext))
        result = self._cipher.cipher_block(state)
        return bytes(result)

    def decrypt(self, ciphertext: bytes) -> bytes:
        state = list(bytearray(ciphertext))
        result = self._cipher.decipher_block(state)
        return bytes(result)
