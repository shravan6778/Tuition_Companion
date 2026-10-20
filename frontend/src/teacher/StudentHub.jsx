import { Link, useParams, useSearchParams } from "react-router-dom";
import { listMembers, listRooms, listTeacherBooks } from "../api/learning";
import Header from "../shared/Header";
import { Async, Tabs, useLoad } from "../shared/ui";
import AssignmentForm from "./AssignmentForm";
import AssignmentList from "./AssignmentList";
import QuizPanel from "./QuizPanel";
import { STUDENT_TABS } from "./StudentTabConfig";
import {
  BriefingTab,
  ProgressTab,
  SessionLogTab,
  WeakAreasTab,
} from "./StudentTabs";
import { useState } from "react";

function WorkTab({ studentId }) {
  const books = useLoad(listTeacherBooks);
  const [n, setN] = useState(0);
  return (
    <div className="stack">
      <Async state={books}>
        {(list) => (
          <AssignmentForm
            books={list}
            studentId={studentId}
            onCreated={() => setN(n + 1)}
          />
        )}
      </Async>
      <AssignmentList studentId={studentId} refreshKey={n} />
    </div>
  );
}

// One student, six tools. The student must be in one of this teacher's rooms (the server enforces it).
export default function StudentHub() {
  const { roomId, studentId } = useParams();
  const [params, setParams] = useSearchParams();
  const tab = STUDENT_TABS.some(([id]) => id === params.get("tab"))
    ? params.get("tab")
    : "work";
  const info = useLoad(async () => {
    const [members, rooms] = await Promise.all([
      listMembers(roomId),
      listRooms(),
    ]);
    return {
      student: members.find((m) => m.id === studentId),
      room: rooms.find((r) => r.id === roomId),
    };
  }, [roomId, studentId]);

  return (
    <>
      <Header
        title={info.data?.student?.name || "Student"}
        subtitle={info.data?.room ? `In ${info.data.room.name}` : ""}
      />
      <div className="container">
        <Link to={`/teacher/rooms/${roomId}`} className="back-link">
          ← Back to the room
        </Link>
        <Async state={info}>
          {({ student }) =>
            student ? (
              <>
                <Tabs
                  tabs={STUDENT_TABS}
                  value={tab}
                  onChange={(t) => setParams({ tab: t }, { replace: true })}
                />
                {tab === "work" && <WorkTab studentId={studentId} />}
                {tab === "briefing" && <BriefingTab studentId={studentId} />}
                {tab === "log" && <SessionLogTab studentId={studentId} />}
                {tab === "progress" && <ProgressTab studentId={studentId} />}
                {tab === "tests" && (
                  <QuizPanel target={{ student_id: studentId }} />
                )}
                {tab === "weak" && <WeakAreasTab studentId={studentId} />}
              </>
            ) : (
              <div className="callout warn">
                This student isn't in this room.
              </div>
            )
          }
        </Async>
      </div>
    </>
  );
}
