package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/maxence-charriere/go-app/v9/docs/src/vectartacomponents"
	"github.com/maxence-charriere/go-app/v9/pkg/app"
	"github.com/maxence-charriere/go-app/v9/pkg/ui"
)

// SearchComponent is a component to display search results.
type SearchComponent struct {
	app.Compo
	Iid     string
	Query   string        // Search query
	Results searchResults // Search results

}

// Render method for the SearchComponent.
func (s *SearchComponent) Render() app.UI {
	return app.Div().
		ID(s.Iid).
		Body(

			app.Form().OnSubmit(s.OnSearchFormSubmit).
				Body(
					app.Aside().Body(
						app.Header().
							ID("search").
							Class("h2").
							Text("Ask a Question"),
						app.P().Body(
							app.Input().
								Style("size", "50").
								Type("text").
								ID("searchInput").
								Value(s.Query).
								OnChange(s.OnInputChange),
							app.P(),
							app.Button().
								Type("submit").
								Class("btn btn-primary").
								Text("Ask Question"),
							app.P(),
							ui.Loader().
								Class("heading").
								Class("fill").
								Loading(s.Results.Status == loading).
								Err(s.Results.Err).
								Label(fmt.Sprintf("Searching ...")),
							app.If(s.Results.Status == loaded,
								vectartacomponents.NewSummaryComponent(s.Results.Summary),
							).Else(),
						),
					),
				),
		)

}

func newSearchPage() *SearchComponent {
	return &SearchComponent{Iid: "searchComponent"}
}

// OnInputChange handles input value changes.
func (s *SearchComponent) OnInputChange(ctx app.Context, e app.Event) {
	// s.Query = ctx.JSSrc().Get("value").String()
}

// OnSearchClick handles search button click.
func (s *SearchComponent) OnSearchFormSubmit(ctx app.Context, e app.Event) {
	e.PreventDefault()
	// Get the value of the search input field
	searchInput := ctx.JSSrc().Get("elements").Call("namedItem", "searchInput")
	if searchInput.Truthy() {
		query := searchInput.Get("value").String()
		// Now you can use the query variable to perform the search
		//handleSearch(ctx, app.Action{Name: "vector_search", Tags: app.Tags{"query": query}})

		ctx.Dispatcher().Context().Async(func() {
			handleSearch(ctx, app.Action{Name: "vector_search", Tags: app.Tags{"query": query}})
			s.load(ctx, query)

		})
	}

}

func (d *SearchComponent) ID(v string) *SearchComponent {
	d.Iid = v
	return d
}

func (d *SearchComponent) OnPreRender(ctx app.Context) {

}

func (d *SearchComponent) OnMount(ctx app.Context) {

}

func (d *SearchComponent) OnUpdate(ctx app.Context) {

}

// load method to fetch search results.
func (s *SearchComponent) load(ctx app.Context, query string) {
	// Define the query key.
	querykey := query
	app.Log("context value %s", querykey)

	// Observe the state based on the query key.
	ctx.ObserveState(searchState(querykey)).
		While(func() bool {
			// Check if search results are loaded or if there's an error.
			return s.Results.Status != loaded && s.Results.Status != loadingErr

		}).OnChange(func() { ctx.ScrollTo(s.Iid) }).Value(&s.Results)
}

const (
	searchEndpoint = "/vsearch"
)

// SearchResult represents a single search result.
type SearchResult struct {
	Text          string  `json:"text"`
	DocumentIndex int     `json:"documentIndex"`
	Score         float64 `json:"score"`
}

// Document represents a single document.
type Document struct {
	ID       string `json:"id"`
	Metadata []struct {
		Name  string `json:"name"`
		Value string `json:"value"`
	} `json:"metadata"`
}

// ResponseData represents the response data from the API.
type ResponseData struct {
	ResponseSet []struct {
		Response []SearchResult `json:"response"`
		Document []Document     `json:"document"`
		Summary  []struct {
			Text string `json:"text"`
		} `json:"summary"`
	} `json:"responseSet"`
	Status  []interface{} `json:"status"`
	Metrics interface{}   `json:"metrics"`
}

func handleSearch(ctx app.Context, a app.Action) {

	query := a.Tags.Get("query")
	if query == "" {
		app.Log("Empty query")
		return
	}

	// Generate state key based on query.
	state := searchState(query)

	// Retrieve search content from state.
	var results searchResults
	//ctx.GetState(state, &results)

	/* Check if search content is already loaded or loading.
	switch results.Status {
	case loading, loaded:
		return
	}
	*/
	// Update search status to loading.

	results.Status = loading
	results.Err = nil
	ctx.SetState(state, results)

	// Perform the search operation.
	// Example: res, err := performSearch(ctx, query)
	// Update results accordingly.

	// For demonstration purposes, we'll simulate a delay.
	// Replace this with your actual search operation.
	go func() {
		url := "https://api.vectara.io/v1/query"
		method := "POST"

		payloadMap := map[string]interface{}{
			"query": []map[string]interface{}{
				{
					"query":        query,
					"queryContext": "",
					"start":        0,
					"numResults":   3,
					"contextConfig": map[string]interface{}{
						"charsBefore":     0,
						"charsAfter":      0,
						"sentencesBefore": 2,
						"sentencesAfter":  2,
					},
					"rerankingConfig": map[string]interface{}{
						"rerankerId": 272725718,
						"mmrConfig": map[string]interface{}{
							"diversityBias": 0,
						},
					},
					"corpusKey": []map[string]interface{}{
						{
							"customerId":     2523211369,
							"corpusId":       14,
							"semantics":      0,
							"metadataFilter": "",
							"lexicalInterpolationConfig": map[string]interface{}{
								"lambda": .025,
							},
							"dim": []interface{}{},
						},
					},
					"summary": []map[string]interface{}{
						{
							"maxSummarizedResults": 5,
							"responseLang":         "auto",
							"summarizerPromptName": "vectara-summary-ext-v1.2.0",
						},
					},
				},
			}}

		payloadJSON, err := mapToJSON(payloadMap)
		if err != nil {
			app.Log("Error converting payload to JSON:", err)
			return
		}

		payload := bytes.NewReader([]byte(payloadJSON))

		client := &http.Client{}
		req, err := http.NewRequest(method, url, payload)
		if err != nil {
			app.Log(err)
			return
		}

		req.Header.Add("Content-Type", "application/json")
		req.Header.Add("Accept", "application/json")
		req.Header.Add("x-api-key", "zqt_lmUmaZymxVXMcg31PLmmzr6nW--8VtXTAgYK3Q")
		req.Header.Add("customer-id", "2523211369")

		res, err := client.Do(req)
		if err != nil {
			app.Log(err)
			return
		}
		defer res.Body.Close()

		body, err := io.ReadAll(res.Body)
		if err != nil {
			app.Log(err)
			return
		}

		app.Log("Response:", string(body))

		var responseData ResponseData
		if err := json.Unmarshal(body, &responseData); err != nil {
			app.Log("Error unmarshalling JSON:", err)
			return
		}

		results.Status = loaded
		//results.Results = body

		app.Log(results.Status)
		app.Log(state)

		// Update search results in the component.
		results.Summary = responseData.ResponseSet[0].Summary[0].Text
		results.RefDocument = responseData.ResponseSet[0].Response
		results.Documents = responseData.ResponseSet[0].Document
		ctx.SetState(state, results)

	}()
}

// mapToJSON converts a map to a JSON string.
func mapToJSON(m map[string]interface{}) (string, error) {
	jsonBytes, err := json.Marshal(m)
	if err != nil {
		return "", err
	}
	return string(jsonBytes), nil
}

// State key generator function.
func searchState(query string) string {
	return query
}

// Helper function to update search results in state.
func updateSearchResults(ctx app.Context, state string, results []byte) {
	// Retrieve current search results.
	var current searchResults
	ctx.GetState(state, &current)

	// Update search results.
	//current.Results = results
	current.Status = loaded

	// Update state with new search results.
	ctx.SetState(state, current)
}

// Data structure to manage search results.
type searchResults struct {
	Status status // Search status (loading, loaded, error, etc.)
	Err    error  // Error if search failed
	//Results     []byte // Search results
	Summary     string
	Documents   []Document
	RefDocument []SearchResult
}
