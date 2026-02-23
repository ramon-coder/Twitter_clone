import mongoose, { Schema, model, models } from "mongoose";

const userSchema = new Schema({
    name: { type: String, required: [true, "El nombre es obligatorio"] },
    email: { type: String, required: [true, "El email es obligatorio"], unique: true },
    password: { type: String, required: [true, "La contraseña es obligatoria"], minlength: 6 },
    dob: { type: Date, required: [true, "La fecha de nacimiento es obligatoria"] },
    joinedDate: { type: Date, default: Date.now },
    nickname: String,
    profilePic: String,
    coverPic: String,
    bio: String,
    location: String,
    followers: { type: Number, default: 0 },
    following: { type: Number, default: 0 },
});

// Optimización para Next.js 15: Evita el error "Cannot overwrite model once compiled"
const User = models.User || model("User", userSchema);

export default User;