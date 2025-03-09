"use client";

import {LoginForm} from "@/components/login-form";
import React from "react";
import {toast} from "sonner";

export default function Page() {
    const [isSubmitting, setIsSubmitting] = React.useState(false);

    function handleSubmit(email: string, password: string) {
        const loginEndpoint =
            process.env.NEXT_PUBLIC_API_ENDPOINT + "/auth/login";
        setIsSubmitting(true);
        const id = toast.loading("Logging in...");
        fetch(loginEndpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({email, password}),
        })
            .then((res) => {
                if (res.ok) {
                    toast.success("Login successful");
                    res.json().then((data) => {
                        const {access_token} = data;
                        document.cookie = `access_token=${access_token}`;
                        window.location.href = "/";
                    });
                } else {
                    toast.error("Login failed");
                }
            })
            .catch((err) => {
                toast.error("Login failed");
                console.error("Login failed", err);
            })
            .finally(() => {
                toast.dismiss(id);
                setIsSubmitting(false);
            });
    }

    return (
        <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
            <div className="w-full max-w-sm">
                <LoginForm
                    submitHandler={handleSubmit}
                    isSubmitting={isSubmitting}
                />
            </div>
        </div>
    );
}
