import NextAuth from "next-auth";
import GitHubProvider from "next-auth/providers/github";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";
import { supabase } from "@/lib/supabase";
import bcrypt from "bcryptjs";

export const authOptions = {
    providers: [
        GitHubProvider({
            clientId: process.env.GITHUB_ID!,
            clientSecret: process.env.GITHUB_SECRET!,
        }),
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
        }),
        CredentialsProvider({
            name: "Credentials",
            credentials: {
                email: { label: "Email", type: "text" },
                password: { label: "Password", type: "password" }
            },
            async authorize(credentials) {
                const { data: user, error } = await supabase
                    .from("users")
                    .select("*")
                    .eq("email", credentials?.email)
                    .single();

                if (error || !user) {
                    throw new Error("Credenciales inválidas");
                }

                if (user.password && await bcrypt.compare(credentials!.password, user.password)) {
                    return {
                        id: user.id,
                        name: user.name,
                        email: user.email,
                        image: user.profilePic,
                    };
                }
                throw new Error("Credenciales inválidas");
            },
        }),
    ],
    callbacks: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        async signIn({ user, account, profile }: { user: any; account: any; profile?: any }) {
            if (account?.provider === "github" || account?.provider === "google") {
                const { data: existingUser } = await supabase
                    .from("users")
                    .select("*")
                    .eq("email", user.email)
                    .single();

                if (!existingUser) {
                    const { data: newUser } = await supabase
                        .from("users")
                        .insert({
                            name: user.name || profile?.login,
                            email: user.email,
                            profilePic: user.image,
                            dob: new Date().toISOString(),
                        })
                        .select()
                        .single();
                    
                    if (newUser) {
                        user.id = newUser.id;
                    }
                } else {
                    user.id = existingUser.id;
                }
            }
            return true;
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        async jwt({ token, user }: { token: any; user?: any }) {
            if (user) {
                token.id = user.id;
            }
            return token;
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        async session({ session, token }: { session: any; token: any }) {
            if (token) {
                session.user.id = token.id as string;
            }
            return session;
        },
    },
    secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };