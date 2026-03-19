from utils.client import get_client
import gradio as gr
import tempfile
from pathlib import Path


client = get_client()

def ask_and_speak_gradio(
    question: str,
    chat_model: str = "gpt-4o-mini",
    tts_model: str = "gpt-4o-mini-tts",
    voice: str = "alloy",
    audio_format: str = "wav",
    system_prompt: str = "You are a concise, helpful assistant. Answer clearly and directly.",
    history=None,
):
    history = history or []  # list of {"role": "...", "content": "..."}
    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": question}
    ]

    chat = client.chat.completions.create(model=chat_model, messages=messages)
    answer_text = chat.choices[0].message.content.strip()

    # Update in-memory history (exclude system prompt)
    new_history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer_text},
    ]

    # TTS to temp file
    suffix = f".{audio_format}"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_path = Path(tmp.name)
    tmp.close()

    with client.audio.speech.with_streaming_response.create(
        model=tts_model,
        voice=voice,
        input=answer_text
    ) as response:
        response.stream_to_file(tmp_path)

    return answer_text, str(tmp_path), new_history

def build_ui():
    with gr.Blocks(title="Ask and Speak") as demo:
        gr.Markdown("### Ask a question, get a spoken answer")
        history_state = gr.State([])

        with gr.Row():
            question = gr.Textbox(label="Question", placeholder="Type your question here...", lines=3)
        with gr.Row():
            chat_model = gr.Dropdown(
                ["gpt-4o-mini", "gpt-4o", "gpt-4o-mini-high"],
                value="gpt-4o-mini",
                label="Chat model"
            )
            tts_model = gr.Dropdown(
                ["gpt-4o-mini-tts", "gpt-4o-tts"],
                value="gpt-4o-mini-tts",
                label="TTS model"
            )
            voice = gr.Dropdown(
                ["alloy", "verse", "aria", "sage"],
                value="alloy",
                label="Voice"
            )
            audio_format = gr.Dropdown(
                ["wav", "mp3", "ogg"],
                value="wav",
                label="Audio format"
            )
        system_prompt = gr.Textbox(
            label="System prompt",
            value="You are a concise, helpful assistant. Answer clearly and directly.",
            lines=2,
            visible=False
        )

        with gr.Row():
            submit = gr.Button("Ask and Speak")
            clear = gr.Button("Clear History")

        answer_out = gr.Textbox(label="Answer", lines=6)
        audio_out = gr.Audio(label="Spoken Answer", autoplay=True, type="filepath")

        submit.click(
            fn=ask_and_speak_gradio,
            inputs=[question, chat_model, tts_model, voice, audio_format, system_prompt, history_state],
            outputs=[answer_out, audio_out, history_state]
        )

        # Clear button resets outputs and history
        clear.click(
            fn=lambda: ("", None, []),
            inputs=[],
            outputs=[answer_out, audio_out, history_state]
        )

    return demo

if __name__ == "__main__":
    app = build_ui()
    app.launch(share=False)