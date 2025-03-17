"use client";

import {Avatar, AvatarFallback, AvatarImage} from "@/components/ui/avatar";
import {Button} from "@/components/ui/button";
import React from "react";
import {getCookie} from "cookies-next/client";
import {jwtDecode, JwtPayload} from "jwt-decode";
import {toast} from "sonner";

type MyJwtPayload = JwtPayload & {
    username: string;
};

export default function Layout({
    children,
}: Readonly<{children: React.ReactNode}>) {
    const [isLoading, setIsLoading] = React.useState(false);
    const [username, setUsername] = React.useState("JD");

    React.useEffect(() => {
        const token = getCookie("access_token")?.valueOf();
        if (!token) {
            window.location.href = "/login";
        }

        const decodedToken = jwtDecode<MyJwtPayload>(token!);
        const username = decodedToken.username;
        setUsername(username);
    }, []);

    function handleLogout() {
        const logoutEndpoint =
            process.env.NEXT_PUBLIC_API_ENDPOINT + "/auth/logout";
        setIsLoading(true);
        const token = getCookie("access_token")!.valueOf();
        const id = toast.loading("Logging out...");
        fetch(logoutEndpoint, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token,
            },
            credentials: "include",
        })
            .then((res) => {
                if (res.ok) {
                    toast.success("Logout successful");
                    document.cookie =
                        "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                    window.location.href = "/login";
                } else {
                    toast.error("Logout failed");
                }
            })
            .catch((err) => {
                toast.error("Logout failed");
                console.error("Logout failed", err);
            })
            .finally(() => {
                toast.dismiss(id);
                setIsLoading(false);
            });
    }

    return (
        <div className="flex flex-col min-h-screen">
            {/* Header */}
            <header className="flex items-center justify-between p-4 border-b">
                <div className="flex items-center space-x-3">
                    <Avatar>
                        <AvatarImage
                            src="https://github.com/shadcn.png"
                            alt="User Avatar"
                        />
                        <AvatarFallback>JD</AvatarFallback>
                    </Avatar>
                    <span className="font-semibold">{username}</span>
                </div>
                <Button
                    variant="destructive"
                    disabled={isLoading}
                    onClick={() => {
                        handleLogout();
                    }}
                >
                    Logout
                </Button>
            </header>
            {/* Main Content */}
            <main className="flex-grow p-4">{children}</main>
        </div>
    );
}
