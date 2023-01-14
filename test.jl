using PlotlyJS, CSV, HTTP, DataFrames
# Read data from a csv
# df = CSV.File(
#     HTTP.get("https://raw.githubusercontent.com/plotly/datasets/master/api_docs/mt_bruno_elevation.csv").body
# ) |> DataFrame

# z_data = Matrix{Float64}(df)'
# (sh_0, sh_1) = size(z_data)

# x = range(0, stop=1, length=sh_0)
# y = range(0, stop=1, length=sh_1)
layout = Layout(
    title="Mt Bruno Elevation", autosize=false,
    width=500, height=500,
    margin=attr(l=65, r=50, b=65, t=90),
    opacity=100
)

graph_range = [-1,1]

length_data = length(graph_range)
z_plane_pos = 0.5*ones((length_data,length_data))

trace = surface(x=graph_range, y=0.5*ones((length_data)), z=z_plane_pos, colorscale=[[0, "#FFDB58"], [1, "#FFDB58"]],  showscale=false)


plot(trace, layout)