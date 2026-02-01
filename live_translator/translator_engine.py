import os
from faster_whisper import WhisperModel

class TranslatorEngine:
    def __init__(self, model_size="medium", device="cpu", compute_type="int8"):
        """
        Initializes the Whisper model for translation.
        """
        print(f"Loading Whisper model '{model_size}'...")
        # For M1, CPU with int8 is fast. For 'small' or 'medium', 
        # using 'float16' on 'cuda' is typical, but on Mac CPU 'int8' is great.
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.target_lang = "en"
        self.previous_text = ""
        print("Model loaded successfully.")

    def set_target_lang(self, lang):
        self.target_lang = lang

    def translate_audio(self, audio_data, source_lang=None):
        """
        Translates audio data to the target language.
        """
        # task="translate" will translate any language to English
        task = "translate" if self.target_lang == "en" else "transcribe"
        
        segments, info = self.model.transcribe(
            audio_data, 
            task=task, 
            language=source_lang,
            beam_size=5,
            vad_filter=True,
            # Accuracy Boost: Condition on previous text to keep context
            initial_prompt=self.previous_text[-200:] if self.previous_text else None,
            word_timestamps=False,
            vad_parameters=dict(min_silence_duration_ms=700)
        )
        
        segment_list = list(segments)
        full_text = " ".join([s.text for s in segment_list]).strip()
        
        if full_text:
            self.previous_text += " " + full_text
            # Keep context buffer manageable
            if len(self.previous_text) > 1000:
                self.previous_text = self.previous_text[-1000:]

        if self.target_lang == "en":
            return full_text, info.language

        # Case 2: Target is Thai
        if not full_text:
            return "", info.language

        if info.language == "th":
            return full_text, "th"

        return self._translate_to_thai(full_text, info.language), info.language

    def _translate_to_thai(self, text, source_lang_code):
        # We'll use deep_translator for the text-to-text part as it is more stable.
        try:
            from deep_translator import GoogleTranslator
            # if source_lang_code is None or 'auto', deep_translator handles auto
            source = source_lang_code if source_lang_code else 'auto'
            translated = GoogleTranslator(source=source, target='th').translate(text)
            return translated
        except Exception as e:
            return f"[Translation Error] {text}"

