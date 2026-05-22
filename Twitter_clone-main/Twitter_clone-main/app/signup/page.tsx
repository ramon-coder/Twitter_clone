"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SignUp() {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        dob: "",
        password: "",
        confirmPassword: "",
    });
    const [error, setError] = useState("");
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        if (formData.password !== formData.confirmPassword) {
            setError("Las contraseñas no coinciden");
            return;
        }

        try {
            const res = await fetch("/api/auth/signup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
            });

            const data = await res.json();
            if (res.ok) {
                router.push("/login");
            } else {
                setError(data.message);
            }
        } catch {
            setError("Error en el servidor");
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-black">
            <div className="w-full max-w-md space-y-8 p-8">
                <h1 className="text-3xl font-bold text-center text-white">Crear cuenta</h1>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="text"
                        placeholder="Nombre"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full p-3 bg-gray-800 text-white rounded"
                        required
                    />
                    <input
                        type="email"
                        placeholder="Email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="w-full p-3 bg-gray-800 text-white rounded"
                        required
                    />
                    <input
                        type="date"
                        value={formData.dob}
                        onChange={(e) => setFormData({ ...formData, dob: e.target.value })}
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
                    <input
                        type="password"
                        placeholder="Confirmar contraseña"
                        value={formData.confirmPassword}
                        onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                        className="w-full p-3 bg-gray-800 text-white rounded"
                        required
                    />
                    {error && <p className="text-red-500">{error}</p>}
                    <button type="submit" className="w-full p-3 bg-blue-500 text-white rounded font-bold">
                        Registrarse
                    </button>
                </form>
                <p className="text-center text-gray-400">
                    ¿Ya tienes cuenta?{" "}
                    <a href="/login" className="text-blue-400">Inicia sesión</a>
                </p>
            </div>
        </div>
    );
}