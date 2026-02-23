import { NextResponse } from "next/server";
import connectToDatabase from "@/lib/mongodb";
import User from "@/models/User";
import bcrypt from "bcryptjs";

export async function POST(req: Request) {
    try {
        const { name, email, dob, password, confirmPassword } = await req.json();

        if (password !== confirmPassword) {
            return NextResponse.json({ message: "Las contraseñas no coinciden" }, { status: 400 });
        }

        await connectToDatabase();

        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return NextResponse.json({ message: "El usuario ya existe" }, { status: 400 });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new User({ name, email, dob, password: hashedPassword });
        await newUser.save();

        return NextResponse.json({ message: "Usuario creado" }, { status: 201 });
    } catch (error) {
        return NextResponse.json({ message: "Error en el servidor" }, { status: 500 });
    }
}   