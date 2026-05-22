import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";
import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/options";

export async function POST(req: Request) {
    try {
        const session = await getServerSession(authOptions);
        if (!session || !session.user) {
            return NextResponse.json({ message: "No autorizado" }, { status: 401 });
        }

        const { tweetId, action } = await req.json();

        const { data: tweet, error: fetchError } = await supabase
            .from("tweets")
            .select("*")
            .eq("id", tweetId)
            .single();

        if (fetchError || !tweet) {
            return NextResponse.json({ message: "Tweet no encontrado" }, { status: 404 });
        }

        const userId = session.user.id;
        const likes = tweet.likes || [];
        const retweets = tweet.retweets || [];

        if (action === "like") {
            const likeIndex = likes.indexOf(userId);
            if (likeIndex > -1) {
                likes.splice(likeIndex, 1);
            } else {
                likes.push(userId);
            }
        } else if (action === "retweet") {
            const retweetIndex = retweets.indexOf(userId);
            if (retweetIndex > -1) {
                retweets.splice(retweetIndex, 1);
            } else {
                retweets.push(userId);
            }
        }

        const { data: updatedTweet } = await supabase
            .from("tweets")
            .update({ likes, retweets })
            .eq("id", tweetId)
            .select()
            .single();

        return NextResponse.json({ 
            likes: updatedTweet?.likes?.length || 0, 
            retweets: updatedTweet?.retweets?.length || 0 
        });
    } catch {
        return NextResponse.json({ message: "Error en la acción" }, { status: 500 });
    }
}