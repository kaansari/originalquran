package vectartacomponents

import (
	"strconv"
	"strings"

	"github.com/maxence-charriere/go-app/v9/pkg/app"
)

// SummaryWithLinks is a component that renders summary text with links
type SummaryWithLinks struct {
	app.Compo
	SummaryText string
}

// Render renders the component
func (s *SummaryWithLinks) Render() app.UI {
	// Split the summary text into segments by finding reference numbers
	segments := splitByRefNumber(s.SummaryText)

	// Render each segment as a div
	divs := make([]app.UI, len(segments))
	for i, segment := range segments {
		divs[i] = segment
	}

	// Render the list of divs
	return app.Div().Body(divs...)
}

// splitByRefNumber splits the summary text by reference numbers
func splitByRefNumber(text string) []app.UI {
	// Define the separator string as "[number]"
	separator := "["

	// Split the text by the separator
	parts := strings.Split(text, separator)

	// Initialize the result with the first part
	result := []app.UI{app.Text(parts[0])}

	// Iterate over the remaining parts and append them to the result
	for i := 1; i < len(parts); i++ {
		// Find the index of the closing bracket "]"
		index := strings.Index(parts[i], "]")
		if index != -1 {
			// Extract the reference number
			refNumberStr := parts[i][:index]
			refNumber, err := strconv.Atoi(refNumberStr)
			app.Log(refNumber)
			if err != nil {
				// If conversion fails, append the part as is
				result = append(result, app.Text(parts[i]))
			} else {
				// Render the reference number and the remaining text separately
				refDiv := app.A().Href(refNumberStr).Body().Text(refNumberStr)
				textDiv := app.Text(parts[i][index+1:])
				result = append(result, refDiv, textDiv)
			}
		} else {
			// If closing bracket not found, append the part as is
			result = append(result, app.Text(parts[i]))
		}
	}

	return result
}

func NewSummaryComponent(summary string) *SummaryWithLinks {

	return &SummaryWithLinks{
		SummaryText: summary,
	}

}
