"use client";

import {useEffect} from "react";

export default function Page() {
    useEffect(() => {
        const apiEndpoint = process.env.NEXT_PUBLIC_API_ENDPOINT;
        const refreshEndpoint = apiEndpoint + "/auth/refresh";
        fetch(refreshEndpoint, {
            method: "GET",
            credentials: "include",
        }).then((res) => {
            if (res.ok) {
                res.json().then((data) => {
                    const {access_token} = data;
                    document.cookie = `access_token=${access_token}`;
                    window.location.href = "/";
                });
            } else {
                console.error("Refresh token failed");
                window.location.href = "/refresh-error";
            }
        });
    }, []);

    return (
        <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
            <div className="w-full max-w-sm"></div>
        </div>
    );
}
