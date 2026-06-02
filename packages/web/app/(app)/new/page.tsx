import { Phase1Form } from "@/components/interview/Phase1Form";

export default function NewProjectPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-1">New architecture spec</h1>
        <p className="text-zinc-400 text-sm">
          Answer 7 quick questions, then Claude will interview you for details.
        </p>
      </div>
      <Phase1Form />
    </div>
  );
}
