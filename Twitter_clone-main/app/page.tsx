"use client";

import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

interface Tweet {
    id: string;
    content: string;
    author: {
        name: string;
        nickname?: string;
        profilePic?: string;
    } | null;
    created_at: string;
    likes: string[];
    retweets: string[];
}

export default function Home() {
    const { status } = useSession();
    const router = useRouter();
    const [tweets, setTweets] = useState<Tweet[]>([]);
    const [newTweet, setNewTweet] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (status === "unauthenticated") {
            router.push("/login");
        }
    }, [status, router]);

    const loadTweets = useCallback(async () => {
        const res = await fetch("/api/tweets");
        const data = await res.json();
        setTweets(data);
    }, []);

    useEffect(() => {
        if (status === "authenticated") {
            loadTweets();
        }
    }, [status, loadTweets]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newTweet.trim()) return;
        
        setLoading(true);
        const res = await fetch("/api/tweets", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: newTweet }),
        });
        
        if (res.ok) {
            setNewTweet("");
            loadTweets();
        }
        setLoading(false);
    };

    const handleLike = async (tweetId: string) => {
        await fetch("/api/tweets/action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tweetId, action: "like" }),
        });
        loadTweets();
    };

    if (status === "loading") {
        return <div className="flex min-h-screen items-center justify-center bg-black text-white">Cargando...</div>;
    }

    return (
        <div className="min-h-screen bg-black text-white">
            <header className="border-b border-gray-800 p-4 flex justify-between items-center">
                <h1 className="text-xl font-bold">Twitter Clone</h1>
                <button onClick={() => signOut()} className="text-blue-400">Cerrar sesión</button>
            </header>
            
            <main className="max-w-2xl mx-auto p-4">
                <form onSubmit={handleSubmit} className="mb-6">
                    <textarea
                        value={newTweet}
                        onChange={(e) => setNewTweet(e.target.value)}
                        placeholder="¿Qué estás pensando?"
                        className="w-full p-3 bg-gray-800 rounded resize-none"
                        rows={3}
                        maxLength={280}
                    />
                    <div className="flex justify-between items-center mt-2">
                        <span className="text-gray-400 text-sm">{newTweet.length}/280</span>
                        <button
                            type="submit"
                            disabled={loading || !newTweet.trim()}
                            className="px-4 py-1 bg-blue-500 rounded font-bold disabled:opacity-50"
                        >
                            Twittear
                        </button>
                    </div>
                </form>

                <div className="space-y-4">
                    {tweets.map((tweet) => (
                        <div key={tweet.id} className="border-b border-gray-800 pb-4">
                            <div className="flex gap-3">
                                <div className="w-12 h-12 rounded-full bg-gray-700 flex items-center justify-center">
                                    {tweet.author?.profilePic ? (
                                        // eslint-disable-next-line @next/next/no-img-element
                                        <img
                                            src={tweet.author.profilePic}
                                            alt={tweet.author.name}
                                            className="w-12 h-12 rounded-full"
                                        />
                                    ) : (
                                        <span className="text-xs">👤</span>
                                    )}
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold">{tweet.author?.name}</span>
                                        {tweet.author?.nickname && (
                                            <span className="text-gray-400">@{tweet.author.nickname}</span>
                                        )}
                                    </div>
                                    <p className="mt-1">{tweet.content}</p>
                                    <div className="flex gap-6 mt-2 text-gray-400 text-sm">
                                        <button
                                            onClick={() => handleLike(tweet.id)}
                                            className="hover:text-red-500"
                                        >
                                            ❤ {tweet.likes?.length || 0}
                                        </button>
                                        <button className="hover:text-green-500">🔁 {tweet.retweets?.length || 0}</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
}