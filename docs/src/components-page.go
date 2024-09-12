//ourteam
package main

import (
	"github.com/maxence-charriere/go-app/v9/pkg/analytics"
	"github.com/maxence-charriere/go-app/v9/pkg/app"
)

type componentsPage struct {
	app.Compo
}

func newComponentsPage() *componentsPage {
	return &componentsPage{}
}

func (p *componentsPage) OnPreRender(ctx app.Context) {
	p.initPage(ctx)
}

func (p *componentsPage) OnNav(ctx app.Context) {
	p.initPage(ctx)
}

func (p *componentsPage) initPage(ctx app.Context) {
	ctx.Page().SetTitle("Our Team")
	ctx.Page().SetDescription("Our Team")
	analytics.Page("Our Team", nil)
}

func (p *componentsPage) Render() app.UI {
	return newPage().
		Title("Our Team").
		//Icon(gridSVG).
		Content(
			newRemoteMarkdownDoc().Src("/web/documents/ourteam.md"),
		)
}
