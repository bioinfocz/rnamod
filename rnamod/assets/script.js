renderChart = (json, chartId) => {
   let range = json.length / 50
   let by = [1, 5, 10, 50, 100, 500, 1000, 2000].find(i => i > range)
   let position = by
   let values = [1, position]

   while (position < json.length) {
      position += by
      values.push(position)
   }

   c3.generate({
      bindto: `#${chartId}`,
      data: {
         json: json,
         keys: {
            x: "position",
            value: ["coverage", "stops_coverage_relative", "errors_relative"],
         },
         axes: {
            coverage: "y",
            stops_coverage_relative: "y2",
            errors_relative: "y2",
         },
         names: {
            coverage: "Coverage",
            stops_coverage_relative: "Stops (in %)",
            errors_relative: "Errors (in %)",
         },
         type: "step",
      },
      axis: {
         x: {
            tick: {
               culling: false,
               values: values,
            },
         },
         y2: {
            show: true,
            min: 0,
            padding: 0,
            max: 100,
            default: [0, 100]
         },
         y: {
            min: 0,
            // max: 100,
            padding: 0
         }
      },
      // subchart: {
      //  show: true
      // }
   })
}
