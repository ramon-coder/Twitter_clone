"use client";

import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Login() {
    const [formData, setFormData] = useState({ email: "", password: "" });
    const [error, setError] = useState("");
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        const result = await signIn("credentials", {
            email: formData.email,
            password: formData.password,
            redirect: false,
        });

        if (result?.error) {
            setError("Credenciales inválidas");
        } else {
            router.push("/");
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-black">
            <div className="w-full max-w-md space-y-8 p-8">
                <h1 className="text-3xl font-bold text-center text-white">Iniciar sesión</h1>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="email"
                        placeholder="Email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="w-full p-3 bg-gray-800 text-white rounded"
                        required
                    />
                    <input
                        type="password"
                        placeholder="Contraseña"
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        className="w-full p-3 bg-gray-800 text-white rounded"
                        required
                    />
                    {error && <p className="text-red-500">{error}</p>}
                    <button type="submit" className="w-full p-3 bg-blue-500 text-white rounded font-bold">
                        Entrar
                    </button>
                </form>
                <div className="space-y-2">
                    <button
                        onClick={() => signIn("github")}
                        className="w-full p-3 bg-gray-700 text-white rounded"
                    >
                        Continuar con GitHub
                    </button>
                    <button
                        onClick={() => signIn("google")}
                        className="w-full p-3 bg-gray-700 text-white rounded"
                    >
                        Continuar con Google
                    </button>
                </div>
                <p className="text-center text-gray-400">
                    ¿No tienes cuenta?{" "}
                    <a href="/signup" className="text-blue-400">Regístrate</a>
                </p>
            </div>
        </div>
    );
}