import gradio as gr
from dotenv import load_dotenv
from agents import Runner
from research_manager import ResearchManager
from confirmationQ_agent import confirmationQ_agent

load_dotenv(override=True)

ORIGINAL_LABEL = "What topic would you like to research?"


async def run(query: str, phase: str, original_query: str, clarifying_question: str):
    query = (query or "").strip()

    if phase == "ask":
        if not query:
            yield (
                gr.update(),
                gr.update(),
                "Please enter a research topic first.",
                "ask",
                "",
                "",
            )
            return

        result = await Runner.run(confirmationQ_agent, f"Query: {query}")
        question = result.final_output.question
        yield (
            gr.update(value="", label=question),
            gr.update(value="Confirm"),
            f"**Original query:** {query}\n\n{question}\n\nType A, B, or C (or your answer) and click Confirm.",
            "research",
            query,
            question,
        )
        return

    # phase == "research"
    if not query:
        yield (
            gr.update(),
            gr.update(),
            "Please answer the clarifying question, then click Confirm.",
            "research",
            original_query,
            clarifying_question,
        )
        return

    combined = (
        f"Original query: {original_query}\n"
        f"Clarifying question: {clarifying_question}\n"
        f"User answer: {query}"
    )
    yield (
        gr.update(interactive=False),
        gr.update(value="Researching...", interactive=False),
        "Starting research...",
        "research",
        original_query,
        clarifying_question,
    )

    report_text = ""
    async for status in ResearchManager().run(combined):
        report_text = status
        yield gr.update(), gr.update(), status, "research", original_query, clarifying_question

    yield (
        gr.update(value="", label=ORIGINAL_LABEL, interactive=True),
        gr.update(value="Run", interactive=True),
        report_text,
        "ask",
        "",
        "",
    )


with gr.Blocks() as ui:
    phase = gr.State("ask")
    original_query = gr.State("")
    clarifying_question = gr.State("")

    query_textbox = gr.Textbox(label=ORIGINAL_LABEL)
    run_button = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")

    inputs = [query_textbox, phase, original_query, clarifying_question]
    outputs = [query_textbox, run_button, report, phase, original_query, clarifying_question]

    run_button.click(run, inputs=inputs, outputs=outputs)
    query_textbox.submit(run, inputs=inputs, outputs=outputs)

ui.launch(theme=gr.themes.Default(primary_hue="sky"))
