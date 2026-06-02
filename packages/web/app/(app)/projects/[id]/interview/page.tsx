import { Phase2Chat } from "@/components/interview/Phase2Chat";

export default async function InterviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <Phase2Chat projectId={id} />;
}
