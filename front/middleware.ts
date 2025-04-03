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
    matcher: [
        "/",
        "/login",
        "/persons",
        "/signup",
        "/refresh",
        "/refresh-error",
    ],
};

async function auth(request: NextRequest) {
    console.log("from request", request.url);

    if (
        request.nextUrl.pathname === "/refresh" ||
        request.nextUrl.pathname === "/login" ||
        request.nextUrl.pathname === "/signup"
    ) {
        console.log("Skipping auth for refresh, login, or signup");
        return NextResponse.next();
    }

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
            if (pathname !== "/persons") {
                return NextResponse.redirect(new URL("/persons", request.url));
            }

            return NextResponse.next();
        }

        console.log("Access token invalid");
        cookieStore.delete("access_token");
    } else {
        console.log("Access token not found");
    }

    if (pathname !== "/refresh-error") {
        console.log("Redirecting to refresh");
        return NextResponse.redirect(new URL("/refresh", request.url));
    }

    console.log("Refresh error, redirecting to login");
    return NextResponse.redirect(new URL("/login", request.url));
}
