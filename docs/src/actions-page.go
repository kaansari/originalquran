package main

import (
	"github.com/maxence-charriere/go-app/v9/pkg/analytics"
	"github.com/maxence-charriere/go-app/v9/pkg/app"
)

type actionPage struct {
	app.Compo
	path string
}

func newActionPage() *actionPage {
	return &actionPage{}
}

func (p *actionPage) OnPreRender(ctx app.Context) {
	p.initPage(ctx)
}

func (p *actionPage) OnNav(ctx app.Context) {
	p.path = ctx.Page().URL().Path
	p.initPage(ctx)
}

func (p *actionPage) initPage(ctx app.Context) {
	ctx.Page().SetTitle("NOON SPA Services")
	ctx.Page().SetDescription("In the heart of Downtown Chicago with expertese in Botox, Dysport, PRP, Sculptra, facials, Cannula, Microneedling, IV Therapy at 231 S State St. Personalized, results-driven beauty")
	analytics.Page("actions", nil)
}

func (p *actionPage) Render() app.UI {
	// Extract the path from the URL.

	// Construct the source URL for the Markdown document.
	srcURL := "/web/documents" + p.path

	return newPage().
		Title("Greenville Crossing").
		Icon(serviceSVG).
		Content(

			newRemoteMarkdownDoc().Src(srcURL),
		)
}
