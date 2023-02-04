"""
Interactive Dash and Plotly application for viewing 3D bifurcation diagrams.
"""

## Init
using JSON
using PlotlyJS
using Dash
using DataFrames
using StatsBase

files = [
    raw".\testdata\freq_sweeps.json",
    raw".\testdata\volt_sweeps.json",
]

min_res = 0.01  # in Volts

struct Run
    f::Float64
    v::Float64
end


function round_to_res(num)
    return round(num/min_res)*min_res
end

## Parse files
# Each file should be a json containing data collected from runs. Format is a dictionary with:
# {
#     "{{AC Frequency (string)}}": {
#             "{{Voltage (string)}}": [
#                 {{peak (float)},
#                 {{peak (float)},
#                 {{peak (float)},
#                 ...
#             ]
#         }
# }
# For examples check ./testruns/

parsed = Dict()
countlist = []

for file in files
    f = open(file, "r")
    parsed_file = JSON.parse(f)
    
    for k in keys(parsed_file)
        if !(k in keys(parsed))
            parsed[k] = Dict()
        end

        for j in keys(parsed_file[k])
            if !(j in keys(parsed[k]))
                parsed[k][j] = []
            end

            rounded = map(round_to_res, parsed_file[k][j])
            counter = countmap(rounded)

            append!(parsed[k][j], collect(keys(counter)))
        end
    end

    close(f)
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
    for z in unique(parsed[string(run.f)][string(run.v)])
        append!(xs, [run.f])
        append!(ys, [run.v])
        append!(zs, [z])
    end
end

df = DataFrame(f=xs,v=ys,z=zs)

## Plot

function gen_3d_plot(df, freq, volt)
    marker = attr(
        size = 0.5,
        color=:black
    )
    
    volt_surface = mesh3d(
        x=[minimum(df.f), maximum(df.f), minimum(df.f), maximum(df.f)],
        y=[volt, volt, volt, volt],
        z=[minimum(df.z), minimum(df.z), maximum(df.z), maximum(df.z)],
        opacity=0.2,
        # Intensity of each vertex, which will be interpolated and color-coded
        intensity=[0.5, 0.5],
        # i, j and k give the vertices of triangles
        # here we represent the 4 triangles of the tetrahedron surface
        i=[0, 0, 0, 1],
        j=[1, 2, 3, 2],
        k=[2, 3, 1, 3],
        showscale=false
    )

    freq_surface = mesh3d(
        x=[freq, freq, freq, freq],
        y=[minimum(df.v), maximum(df.v), minimum(df.v), maximum(df.v)],
        z=[minimum(df.z), minimum(df.z), maximum(df.z), maximum(df.z)],
        opacity=0.2,
        # Intensity of each vertex, which will be interpolated and color-coded
        intensity=[1, 1, 1, 1],
        # i, j and k give the vertices of triangles
        # here we represent the 4 triangles of the tetrahedron surface
        i=[0, 0, 0, 1],
        j=[1, 2, 3, 2],
        k=[2, 3, 1, 3],
        showscale=false
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

    # if isnothing(click_data)
    return Plot([volt_surface, freq_surface, trace], layout)
    # end
end

function f_focus(df, freq)
    filtered = filter(row -> row[:f] == freq, df)
    trace = scatter(x=filtered.v, y=filtered.z, mode="markers",
                        marker=attr(
                            size = 3,
                            color= :black
                        ))
    return Plot(trace, Layout(title = "Frequency = $freq", template = :plotly_dark))
end

function v_focus(df, volt)
    filtered = filter(row -> row[:v] == volt, df)
    trace = scatter(x=filtered.f, y=filtered.z, mode="markers",
                        marker=attr(
                            size = 3,
                            color = :black
                        ))
    return Plot(trace, Layout(title = "Voltage = $volt", template = :plotly_dark))
end

## App

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

app.layout = html_div(style=dark_mode_style) do
    (html_div(style=vertical_graph_style) do 
        dcc_graph(id = "input-bi-map", figure=gen_3d_plot(df, nothing, nothing)),
        html_div(
            children = [               
                "Frequency: ",
                dcc_input(id = "freq-input", value = "25000", type = "text"),
                "Voltage: ",
                dcc_input(id = "volt-input", value = "6.2", type = "text")
            ]
        )
    end),
    
    (html_div(id = "plane-divs") do
        dcc_graph(id = "freq-bi-map", style=inline_graph_style, figure=f_focus(df, 25000)),
        dcc_graph(id = "volt-bi-map", style=inline_graph_style, figure=v_focus(df, 6.2))
    end)
end

callback!(
    app,
    Output("freq-bi-map", "figure"),
    Input("freq-input", "value")
) do f
    if isnothing(f)
        return Plot()
    end
    
    if typeof(f) == String
        f = parse(Float64, f)
    end 
    
    return f_focus(df, f)
end

callback!(
    app,
    Output("volt-bi-map", "figure"),
    Input("volt-input", "value")
) do v
    if isnothing(v)
        return Plot()
    end
    
    if typeof(v) == String
        v = parse(Float64, v)
    end 

    return v_focus(df, v)
end


callback!(
    app,
    Output("input-bi-map", "figure"),
    Input("freq-input", "value"),
    Input("volt-input", "value")
) do f, v
    if typeof(f) == String
        f = parse(Float64, f)
    end
    
    if typeof(v) == String
        v = parse(Float64, v)
    end
    
    return gen_3d_plot(df, f, v)
end

run_server(app, "0.0.0.0",10321, debug = true)
