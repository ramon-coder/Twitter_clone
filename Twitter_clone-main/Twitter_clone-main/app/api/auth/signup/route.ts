import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";
import bcrypt from "bcryptjs";

export async function POST(req: Request) {
    try {
        const { name, email, dob, password, confirmPassword } = await req.json();

        if (password !== confirmPassword) {
            return NextResponse.json({ message: "Las contraseñas no coinciden" }, { status: 400 });
        }

        const { data: existingUser } = await supabase
            .from("users")
            .select("*")
            .eq("email", email)
            .single();

        if (existingUser) {
            return NextResponse.json({ message: "El usuario ya existe" }, { status: 400 });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        
        const { error } = await supabase
            .from("users")
            .insert({ name, email, dob, password: hashedPassword });

        if (error) {
            return NextResponse.json({ message: "Error al crear usuario" }, { status: 500 });
        }

        return NextResponse.json({ message: "Usuario creado" }, { status: 201 });
    } catch {
        return NextResponse.json({ message: "Error en el servidor" }, { status: 500 });
    }
}