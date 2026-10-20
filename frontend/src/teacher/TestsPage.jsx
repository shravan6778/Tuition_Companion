import Header from "../shared/Header";
import QuizPanel from "./QuizPanel";

export default function TestsPage() {
  return (
    <>
      <Header title="Tests" subtitle="Generate a test for a chapter, check the answer key, then give it to a room." />
      <div className="container"><QuizPanel /></div>
    </>
  );
}
