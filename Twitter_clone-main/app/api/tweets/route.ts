import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";
import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/options";

export async function GET() {
    try {
        const { data: tweets, error } = await supabase
            .from("tweets")
            .select(`
                *,
                author:users(id, name, nickname, profilePic)
            `)
            .order("created_at", { ascending: false })
            .limit(50);

        if (error) throw error;
        
        return NextResponse.json(tweets || []);
    } catch {
        return NextResponse.json({ message: "Error al obtener tweets" }, { status: 500 });
    }
}

export async function POST(req: Request) {
    try {
        const session = await getServerSession(authOptions);
        if (!session || !session.user) {
            return NextResponse.json({ message: "No autorizado" }, { status: 401 });
        }

        const { content, parentTweet, images } = await req.json();
        
        if (!content || content.length > 280) {
            return NextResponse.json({ message: "Contenido inválido" }, { status: 400 });
        }

        const { data: tweet, error } = await supabase
            .from("tweets")
            .insert({
                content,
                author_id: session.user.id,
                parent_tweet: parentTweet || null,
                images: images || [],
            })
            .select(`
                *,
                author:users(id, name, nickname, profilePic)
            `)
            .single();

        if (error) throw error;

        return NextResponse.json(tweet, { status: 201 });
    } catch {
        return NextResponse.json({ message: "Error al crear tweet" }, { status: 500 });
    }
}