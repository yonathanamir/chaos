## 

using JSON
using PlotlyJS
using Dash
using DataFrames


f = open("C:\\Users\\Yonathan\\Downloads\\run.json", "r")
parsed = JSON.parse(f)
close(f)
# print(parsed)

struct Run
    f::Float64
    v::Float64
end

runs = Run[]
freqs = collect(parse(Float64, f) for f in keys(parsed))

for f in freqs
    vs = collect(parse(Float64, v) for v in keys(parsed[string(f)]))
    for v in vs
        append!(runs, [Run(f, v)])
    end
end

xs = []
ys = []
zs = []
for run in runs
    for z in parsed[string(run.f)][string(run.v)]
        append!(xs, [run.f])
        append!(ys, [run.v])
        append!(zs, [z])
    end
end

df = DataFrame(f=xs,v=ys,z=zs)

## Plot

function gen_3d_plot(df, click_data)
    marker = attr(
        size = 2,
        color = :black
    )

    trace = scatter3d(x=df.f,y=df.v,z=df.z, marker=marker, mode="markers")
    layout = Layout(
        title = "3D View",
        scene = attr(
            xaxis_title = "Frequency (Hz)",
            yaxis_title = "Input Voltage (V)",
            zaxis_title = "Diode Voltages (V)"
        )
    )

    if isnothing(click_data)
        return Plot(trace, layout)

    clicked_freq = click_data["points"][1].x
    clicked_volt = click_data["points"][1].y

    freq_range = [minimum(df.f), maximum(df.f)]
    volt_range = [minimum(df.v), maximum(df.v)]
    z_range = [minimum(df.z), maximum(df.z)]

    trace = surface(x=freq_range, y=clicked_volt*ones(), z=volt_range, colorscale=[[0, "#FFDB58"], [1, "#FFDB58"]],  showscale=false)



        
    return plt
end

app = dash()

inline_graph_style = Dict(
    "width" => "49%",
    "height" => "50%",
    "display" => "inline-block",
    "padding" => "0 20"
)

vertical_graph_style = Dict(
    "height" => "50%",
    "display" => "inline-block",
)

dark_mode_style = Dict(
    "backgroundColor" => "#2a2a2a", 
    "color" => "white"
)

# style=vertical_graph_style
app.layout = html_div(style=dark_mode_style) do
    (html_div(style=vertical_graph_style) do 
        dcc_graph(id = "input-bi-map", figure=gen_3d_plot(df))
    end),
    
    (html_div(id = "plane-divs") do
        dcc_graph(id = "freq-bi-map", style=inline_graph_style),
        dcc_graph(id = "volt-bi-map", style=inline_graph_style)
    end)
end

callback!(
    app,
    Output("freq-bi-map", "figure"),
    Input("input-bi-map", "clickData"),
) do click_data
    if isnothing(click_data)
        return Plot()
    end
    freq = click_data["points"][1].x
    volt = click_data["points"][1].y

    filtered = filter(row -> row[:f] == freq, df)
    trace = scatter(x=filtered.v, y=filtered.z, mode="markers",
                        marker=attr(
                            size = 3,
                            color = :black
                        ))
    return Plot(trace, Layout(title = "Frequency = $freq", template = :plotly_dark))
end

callback!(
    app,
    Output("volt-bi-map", "figure"),
    Input("input-bi-map", "clickData"),
) do click_data
    if isnothing(click_data)
        return Plot()
    end

    freq = click_data["points"][1].x
    volt = click_data["points"][1].y

    filtered = filter(row -> row[:v] == volt, df)
    trace = scatter(x=filtered.f, y=filtered.z, mode="markers",
                        marker=attr(
                            size = 3,
                            color = :black
                        ))
    return Plot(trace, Layout(title = "Voltage = $volt", template = :plotly_dark))
end

run_server(app, "0.0.0.0", debug = true)
