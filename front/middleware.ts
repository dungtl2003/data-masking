// middleware.ts
import {cookies} from "next/headers";
import {NextResponse} from "next/server";
import type {NextRequest} from "next/server";

const allowedOrigins = [process.env.SERVER_ENDPOINT];

const corsOptions = {
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

export async function middleware(request: NextRequest) {
    // Check the origin from the request
    const origin = request.headers.get("origin") ?? "";
    const isAllowedOrigin = allowedOrigins.includes(origin);

    // Handle preflighted requests
    const isPreflight = request.method === "OPTIONS";

    if (isPreflight) {
        const preflightHeaders = {
            ...(isAllowedOrigin && {"Access-Control-Allow-Origin": origin}),
            ...corsOptions,
        };
        return NextResponse.json({}, {headers: preflightHeaders});
    }

    const resp = await auth(request);
    if (isAllowedOrigin) {
        resp.headers.set("Access-Control-Allow-Origin", origin);
    }

    Object.entries(corsOptions).forEach(([key, value]) => {
        resp.headers.set(key, value);
    });
    return resp;
}

// Only run this middleware on these routes
export const config = {
    matcher: ["/", "/login", "/persons", "/signup"],
};

async function auth(request: NextRequest) {
    const apiEndpoint = process.env.API_ENDPOINT;
    const {pathname} = request.nextUrl;
    const authEndpoint = new URL(apiEndpoint + "/auth/authorize");
    const cookieStore = await cookies();
    const accessToken = cookieStore.get("access_token")?.value;

    request.headers.set("Authorization", `Bearer ${accessToken}`);

    if (accessToken) {
        console.log("Access token found");
        const resp = await fetch(authEndpoint, {
            method: "GET",
            headers: request.headers,
        });

        if (resp.status === 200) {
            if (
                pathname === "/login" ||
                pathname === "/signup" ||
                pathname === "/"
            ) {
                return NextResponse.redirect(new URL("/persons", request.url));
            }

            return NextResponse.next();
        }

        cookieStore.delete("access_token");
    }

    const refreshEndpoint = new URL(apiEndpoint + "/auth/refresh");
    const resp = await fetch(refreshEndpoint, {
        method: "GET",
        headers: request.headers,
        credentials: "include",
    });

    if (resp.status === 200) {
        if (
            pathname === "/login" ||
            pathname === "/signup" ||
            pathname === "/"
        ) {
            const {access_token} = await resp.json();
            cookieStore.set("access_token", access_token);
            return NextResponse.redirect(new URL("/persons", request.url));
        }

        return NextResponse.next();
    }

    if (pathname !== "/login" && pathname !== "/signup") {
        return NextResponse.redirect(new URL("/login", request.url));
    }

    return NextResponse.next();
}
