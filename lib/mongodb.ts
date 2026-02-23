import mongoose from "mongoose";

const connectToDatabase = async () => {
    if (mongoose.connection.readyState >= 1) return;
    try {
        await mongoose.connect(process.env.MONGODB_URI!);
    } catch (error) {
        console.error("Error en DB:", error);
    }
};

export default connectToDatabase;