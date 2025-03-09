"use client";

import {SignupForm} from "@/components/signup-form";
import React from "react";
import {toast} from "sonner";

export default function Page() {
    const [isLoading, setIsLoading] = React.useState(false);

    function handleSubmit(
        email: string,
        username: string,
        password: string,
        gender: string,
        city: string,
        phoneNumber: string
    ) {
        const signupEndpoint =
            process.env.NEXT_PUBLIC_API_ENDPOINT + "/persons";
        const payload = {
            email,
            username,
            password,
            gender,
            city,
            phone_number: phoneNumber,
        };
        setIsLoading(true);
        const id = toast.loading("Creating your account...");
        fetch(signupEndpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify(payload),
        })
            .then((response) => {
                if (response.status === 201) {
                    toast.success("Account created successfully!");
                    window.location.href = "/login";
                } else {
                    toast.error("Failed to create account. Please try again.");
                }
            })
            .catch((err) => {
                toast.error("Failed to create account. Please try again.");
                console.error("Failed to create account", err);
            })
            .finally(() => {
                setIsLoading(false);
                toast.dismiss(id);
            });
    }

    return (
        <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
            <div className="w-full max-w-sm">
                <SignupForm
                    submitHandler={handleSubmit}
                    isLoading={isLoading}
                />
            </div>
        </div>
    );
}
