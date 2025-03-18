# DocQuery

Prompt query from any documents (I focus on receipts for my use case). Just upload your file (.jpg, .jpeg, .png) and ask a question. This will yield two results - answer text and image with highlighted answer.

Using LayoutLM model. Initially used Donut, but it doesn't work well with receipts since it does not take into consideration the document layout when processing the image.

This use case explores the OCR and LLM implementation as part of my internship task.
