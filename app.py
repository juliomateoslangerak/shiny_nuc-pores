from shiny import App, render, ui, reactive
# import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.express as px
from shinywidgets import output_widget, register_widget

import numpy as np
from skimage import io
from skimage.feature import peak_local_max

image = io.imread("20230921_RI510_TPR-A488_DAPI_006_SIR_ALX_THR_C0.ome.tiff")

app_ui = ui.page_fluid(
    ui.panel_title("Nuclear pores are cool. Let's count them!"),

    ui.layout_sidebar(

        ui.panel_sidebar(
            ui.input_checkbox("use_min_distance", "Use min distance", False),
            ui.panel_conditional(
                "input.use_min_distance",
                ui.input_slider("min_distance", "Min distance", 1, 20, 3)
            ),
            ui.input_checkbox("use_threshold", "Use threshold", False),
            ui.panel_conditional(
                "input.use_threshold",
                ui.input_radio_buttons("threshold_type", "Threshold type", ["absolute", "relative"]),
                ui.panel_conditional("input.threshold_type == 'relative'",
                                    ui.input_slider("threshold_rel", "Threshold", 0, 1, 0.1)),
                ui.panel_conditional("input.threshold_type == 'absolute'",
                                     ui.input_slider("threshold_abs", "Threshold", 0, 65536, 5000))
            ),
            ui.input_checkbox("exclude_border", "Exclude pores on the border", False),
            ui.input_checkbox("use_num_peaks", "Limit the number of pores", False),
            ui.panel_conditional("input.use_num_peaks", ui.input_numeric("num_peaks", "Maximum number of pores", 500)),
            ui.input_action_button("count", "Count pores")
        ),

        ui.panel_main(
            ui.input_slider("z_position", "Z position", 0, image.shape[0], image.shape[0] // 2),
            ui.input_checkbox("show_pores", "Show detected pores", False),
            output_widget("image_plot"),
            # ui.output_text_verbatim("image_plot")
        )
    )
)


def server(input, output, session):
    image_widget = go.FigureWidget(px.imshow(image[input.z_position(), :, :], color_continuous_scale='gray'))

    register_widget("image_plot", image_widget)

    # @reactive.Effect
    # def _():
    #     scatterplot.data[1].visible = input.show_fit()

    @reactive.Calc
    def count_pores():
        if input.use_min_distance():
            min_distance = input.min_distance()
        else:
            min_distance = 1
        if input.use_threshold() and input.threshold_type() == "absolute":
            threshold_abs = input.threshold_abs()
            threshold_rel = None
        elif input.use_threshold() and input.threshold_type() == "relative":
            threshold_abs = None
            threshold_rel = input.threshold_rel()
        else:
            threshold_abs = None
            threshold_rel = None
        if input.use_num_peaks:  # TODO: this is not working
            num_peaks = input.num_peaks()
        else:
            num_peaks = np.inf

        return peak_local_max(
            image,
            min_distance=min_distance,
            threshold_abs=threshold_abs,
            threshold_rel=threshold_rel,
            exclude_border=input.exclude_border(),
            num_peaks=num_peaks,
            p_norm=2
        )


    # @output
    # @render.plot(alt="nuclear pores")
    # # @render.text
    # def image_plot():
    #     input.count()
    #
    #     with reactive.isolate():
    #         peaks = count_pores()
    #
    #     imgplot = plt.imshow(image[input.z_position(), :, :])
    #     imgplot.set_cmap('gray')
    #     # plt.colorbar()
    #     z_peaks = peaks[(peaks[:, 0] == input.z_position())]
    #     imgplot.set_clim(image.min(), image.max())
    #     plt.plot(z_peaks[:, 2], z_peaks[:, 1], 'r.')
    #     # return z_peaks
    #     return imgplot


app = App(app_ui, server)
