# Figure Rules

The `write-paper` skill reads this file before it makes a figure or a plot.
This workflow adapts the retrieve, plan, style, draw, and critique roles of [PaperBanana](https://github.com/dwzhu-pku/PaperBanana) (Zhu et al., arXiv:2601.23265, Apache-2.0).
You perform each role yourself. You do not call an image generation model or an external API. You draw each figure as LaTeX source, so each label stays editable and each value stays checkable.

## 1. Retrieve References

- You open the exemplar papers that `notes/venue-bar.md` lists in `reaper-workspace/papers/`.
- You select one to three exemplar figures of the same type as the new figure. Examples of types are a pipeline, a protocol message flow, a layered stack, and a comparison plot.
- For each selected figure, you record its layout, shapes, colors, line styles, and text size. You do not copy the figure.
- If no exemplar has a figure of the same type, you use the default style in step 3.

## 2. Plan

You write one section for each figure in `reaper-workspace/notes/figure-plans.md`. Each section contains:

- The figure file name, the caption, and the paper labels of the definitions, theorems, or results that the figure shows.
- A layout pattern, for example a pipeline, a layered stack, a control loop, a tree, a hub with spokes, or a message sequence chart.
- Each element and each connection, with its source in the paper text.
- For a plot, the data file, the variable for each axis, and each data point.

Each element and each label must come from the paper text or a data file. You do not add an element without a source.

## 3. Style

You use the style of the selected exemplars. Without exemplars, you use this default style:

- **Background:** You use a white background. You use a light fill only to group the elements of one stage.
- **Color:** You use grayscale and one highlight color for the main result or the attack path. Each color difference also has a line style, marker, or pattern difference, so that the figure stays clear in grayscale print and for readers with color blindness.
- **Shapes:** You use rounded rectangles for processes, rectangles for data, and cylinders only for storage. You use one shape for each concept.
- **Lines:** You use solid arrows for the main flow. You use dashed lines for optional flows and for group borders. You use one line style for each meaning.
- **Text:** You write each variable with the math notation and macros of the paper. You do not put the caption or a legend that repeats the caption in the figure. You do not use icons or cartoon characters in a theory or protocol paper.
- **Plots:** You use a light dashed grid behind the data. You put a marker on each data point of a line. You show variation across runs as a shaded band. You put the legend inside the plot area or label each line directly. You do not use rainbow color maps or 3D effects.

## 4. Draw

- You draw each diagram with TikZ in `figures/<name>.tex`. You load each TikZ library that you use with `\usetikzlibrary` in `main.tex`.
- You draw each plot with `pgfplots` in `figures/<name>.tex`. You read the values from a data file `figures/<name>.dat`, which you copy from the workspace result. You do not type data values into the plot code.
- You set the figure width to `\linewidth` or less. After scaling, the smallest text must be at least the `\footnotesize` size of the document.

## 5. Critique

You do at most three critique rounds for each figure. In each round:

1. You run `make` in `reaper-workspace/report/`.
2. You render the page with the figure as an image, for example with `pdftoppm -png -r 150 -f <page> -l <page> main.pdf page`. You inspect the image when you can read images. If you cannot read images, you inspect the LaTeX source only and report that limitation.
3. You check the content. Each element and connection agrees with the plan and the paper. The figure omits no critical component and adds no element without a source. Each label has the correct spelling. Each example value and each plot value agrees with its source.
4. You check the presentation. No text overlaps another element or goes outside the figure. No line crosses a label. The flow direction is clear. The text is readable at print size. The figure stays clear in grayscale.
5. You correct each defect in the plan and in the figure file.

After three rounds, you report each remaining defect.
