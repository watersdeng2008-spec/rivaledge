"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Channel {
  id: string;
  name: string;
  platform: string;
  username: string;
}

interface Post {
  id: string;
  channelId: string;
  text: string;
  dueAt: string;
  status: string;
}

export default function BufferAdminPage() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Form state
  const [selectedChannel, setSelectedChannel] = useState("");
  const [postText, setPostText] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [dueTime, setDueTime] = useState("13:00");
  const [isThread, setIsThread] = useState(false);
  const [threadTweets, setThreadTweets] = useState(["", "", ""]);
  const [scheduling, setScheduling] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchChannels();
    fetchPosts();
  }, []);

  const fetchChannels = async () => {
    try {
      const res = await fetch("/api/buffer/channels");
      if (!res.ok) {
        const errorData = await res.json();
        console.error("Channel fetch error:", errorData);
        throw new Error(errorData.detail || "Failed to fetch channels");
      }
      const data = await res.json();
      setChannels(data.channels || []);
      if (data.channels?.length > 0) {
        setSelectedChannel(data.channels[0].id);
      }
    } catch (err: any) {
      console.error("Fetch channels error:", err);
      setError(err.message || "Failed to load channels");
    }
  };

  const fetchPosts = async () => {
    try {
      const res = await fetch("/api/buffer/posts");
      if (!res.ok) throw new Error("Failed to fetch posts");
      const data = await res.json();
      setPosts(data.posts || []);
    } catch (err) {
      console.error("Failed to load posts", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    setScheduling(true);
    setMessage("");

    try {
      if (isThread) {
        // Schedule thread
        const tweets = threadTweets.filter(t => t.trim());
        if (tweets.length === 0) throw new Error("No tweets to schedule");

        const startAt = new Date(`${dueDate}T${dueTime}:00Z`);
        
        const res = await fetch("/api/buffer/schedule-thread", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            channel_id: selectedChannel,
            tweets,
            start_at: startAt.toISOString(),
          }),
        });

        if (!res.ok) throw new Error("Failed to schedule thread");
        const data = await res.json();
        setMessage(`Scheduled ${data.count} tweets successfully!`);
      } else {
        // Schedule single post
        const dueAt = new Date(`${dueDate}T${dueTime}:00Z`);
        
        const res = await fetch("/api/buffer/schedule", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            channel_id: selectedChannel,
            text: postText,
            due_at: dueAt.toISOString(),
          }),
        });

        if (!res.ok) throw new Error("Failed to schedule post");
        setMessage("Post scheduled successfully!");
      }

      // Reset form and refresh
      setPostText("");
      setThreadTweets(["", "", ""]);
      fetchPosts();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setScheduling(false);
    }
  };

  const handleDelete = async (postId: string) => {
    if (!confirm("Delete this scheduled post?")) return;
    
    try {
      const res = await fetch(`/api/buffer/posts/${postId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete");
      fetchPosts();
    } catch (err) {
      alert("Failed to delete post");
    }
  };

  const addTweetField = () => {
    setThreadTweets([...threadTweets, ""]);
  };

  const updateTweet = (index: number, value: string) => {
    const newTweets = [...threadTweets];
    newTweets[index] = value;
    setThreadTweets(newTweets);
  };

  const formatDate = (isoString: string) => {
    return new Date(isoString).toLocaleString();
  };

  const getChannelName = (channelId: string) => {
    const channel = channels.find(c => c.id === channelId);
    return channel ? `${channel.name} (${channel.platform})` : channelId;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <div className="text-slate-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Nav */}
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-slate-400 hover:text-white">
              ← Back to Dashboard
            </Link>
          </div>
          <span className="text-xl font-bold text-blue-400">Buffer Admin</span>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold mb-8">Social Media Automation</h1>

        {error && (
          <div className="bg-red-900/50 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-8">
          {/* Schedule Form */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-6">Schedule New Post</h2>

            <form onSubmit={handleSchedule} className="space-y-4">
              {/* Channel Select */}
              <div>
                <label className="block text-sm text-slate-400 mb-2">Channel</label>
                <select
                  value={selectedChannel}
                  onChange={(e) => setSelectedChannel(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white"
                  required
                >
                  {channels.map((channel) => (
                    <option key={channel.id} value={channel.id}>
                      {channel.name} ({channel.platform})
                    </option>
                  ))}
                </select>
              </div>

              {/* Thread Toggle */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="isThread"
                  checked={isThread}
                  onChange={(e) => setIsThread(e.target.checked)}
                  className="rounded bg-slate-800 border-slate-700"
                />
                <label htmlFor="isThread" className="text-sm text-slate-400">
                  Schedule as Twitter thread
                </label>
              </div>

              {/* Post Content */}
              {isThread ? (
                <div className="space-y-3">
                  <label className="block text-sm text-slate-400">Thread Tweets</label>
                  {threadTweets.map((tweet, index) => (
                    <div key={index} className="relative">
                      <textarea
                        value={tweet}
                        onChange={(e) => updateTweet(index, e.target.value)}
                        placeholder={`Tweet ${index + 1}`}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white h-20 resize-none"
                        maxLength={280}
                      />
                      <span className="absolute bottom-2 right-2 text-xs text-slate-500">
                        {tweet.length}/280
                      </span>
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={addTweetField}
                    className="text-blue-400 text-sm hover:text-blue-300"
                  >
                    + Add another tweet
                  </button>
                </div>
              ) : (
                <div className="relative">
                  <label className="block text-sm text-slate-400 mb-2">Post Content</label>
                  <textarea
                    value={postText}
                    onChange={(e) => setPostText(e.target.value)}
                    placeholder="What's on your mind?"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white h-32 resize-none"
                    maxLength={280}
                    required={!isThread}
                  />
                  <span className="absolute bottom-2 right-2 text-xs text-slate-500">
                    {postText.length}/280
                  </span>
                </div>
              )}

              {/* Schedule Time */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Date</label>
                  <input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Time (UTC)</label>
                  <input
                    type="time"
                    value={dueTime}
                    onChange={(e) => setDueTime(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white"
                    required
                  />
                </div>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={scheduling}
                className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white py-3 rounded-lg font-semibold transition-colors"
              >
                {scheduling ? "Scheduling..." : isThread ? "Schedule Thread" : "Schedule Post"}
              </button>

              {message && (
                <div className={`text-sm ${message.includes("Error") ? "text-red-400" : "text-green-400"}`}>
                  {message}
                </div>
              )}
            </form>
          </div>

          {/* Scheduled Posts */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-6">Scheduled Posts ({posts.length})</h2>

            {posts.length === 0 ? (
              <div className="text-slate-500 text-center py-8">
                No scheduled posts yet.
              </div>
            ) : (
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {posts.map((post) => (
                  <div key={post.id} className="bg-slate-800 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-xs text-blue-400">
                        {getChannelName(post.channelId)}
                      </span>
                      <button
                        onClick={() => handleDelete(post.id)}
                        className="text-red-400 text-xs hover:text-red-300"
                      >
                        Delete
                      </button>
                    </div>
                    <p className="text-sm text-slate-300 mb-2 line-clamp-3">
                      {post.text}
                    </p>
                    <div className="text-xs text-slate-500">
                      {formatDate(post.dueAt)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Connected Channels */}
        <div className="mt-8 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-4">Connected Channels</h2>
          <div className="flex gap-4">
            {channels.map((channel) => (
              <div key={channel.id} className="bg-slate-800 rounded-lg px-4 py-3">
                <div className="font-medium">{channel.name}</div>
                <div className="text-sm text-slate-400">{channel.platform}</div>
                <div className="text-xs text-slate-500">@{channel.username}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
