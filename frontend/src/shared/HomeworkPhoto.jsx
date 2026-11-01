import { useEffect } from "react";
import { submissionPhoto } from "../api/learning";
import { Async, useLoad } from "./ui";

// A handed-in homework photo. The server only serves it to the student who sent it and the teacher who set the task, so it is
// fetched with the session cookie and shown from a temporary object URL (an <img src> to the API would not carry the cookie).
export default function HomeworkPhoto({ path, alt = "Photo of the homework" }) {
  const state = useLoad(() => submissionPhoto(path).then((blob) => URL.createObjectURL(blob)), [path]);
  useEffect(() => {
    const url = state.data;
    return () => { if (url) URL.revokeObjectURL(url); };
  }, [state.data]);
  return (
    <Async state={state}>
      {(url) => (
        <a href={url} target="_blank" rel="noreferrer">
          <img src={url} alt={alt} style={{ maxWidth: "100%", maxHeight: 360, borderRadius: 8, border: "1px solid var(--border)" }} />
        </a>
      )}
    </Async>
  );
}
