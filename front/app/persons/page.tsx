"use client";

import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import React from "react";
import {getCookie} from "cookies-next/client";
import {toast} from "sonner";

interface Person {
    id: number;
    username: string;
    email: string;
    gender: string;
    city: string;
    phone_number: string;
}

export default function Page() {
    const [persons, setPersons] = React.useState<Person[]>([]);

    React.useEffect(() => {
        const personsEndpoint =
            process.env.NEXT_PUBLIC_API_ENDPOINT + "/persons";
        const token = getCookie("access_token")!.valueOf();
        const toastId = toast.loading("Fetching persons...");

        fetch(personsEndpoint, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token,
            },
            credentials: "include",
        })
            .then((response) => {
                if (response.status === 200) {
                    return response.json();
                } else {
                    throw new Error("Failed to fetch persons.");
                }
            })
            .then((data) => {
                setPersons(data);
            })
            .catch((err) => {
                console.error("Failed to fetch persons", err);
            })
            .finally(() => {
                toast.dismiss(toastId);
            });
    }, []);
    return (
        <Table>
            <TableCaption>A list of persons.</TableCaption>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[100px]">ID</TableHead>
                    <TableHead>Username</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Gender</TableHead>
                    <TableHead>City</TableHead>
                    <TableHead>Phone number</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {persons.map((person) => (
                    <TableRow key={person.id}>
                        <TableCell className="font-medium">
                            {person.id}
                        </TableCell>
                        <TableCell>{person.username}</TableCell>
                        <TableCell>{person.email}</TableCell>
                        <TableCell>{person.gender}</TableCell>
                        <TableCell>{person.city}</TableCell>
                        <TableCell>{person.phone_number}</TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    );
}
