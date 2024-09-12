package main

import (
	"github.com/maxence-charriere/go-app/v9/pkg/analytics"
	"github.com/maxence-charriere/go-app/v9/pkg/app"
)

type servicesPage struct {
	app.Compo
}

func newServicesPage() *servicesPage {
	return &servicesPage{}
}

func (p *servicesPage) OnPreRender(ctx app.Context) {
	p.initPage(ctx)
}

func (p *servicesPage) OnNav(ctx app.Context) {
	p.initPage(ctx)
}

func (p *servicesPage) initPage(ctx app.Context) {
	ctx.Page().SetTitle("Floor Plans")
	ctx.Page().SetDescription("Experience modern living in this delightful 1-bedroom, 1-bathroom guest suite plan, boasting a total living area of over 496 square feet.")
	analytics.Page("plans", nil)
}

func (p *servicesPage) Render() app.UI {
	return newPage().
		Title("Floor Plans").
		Icon(serviceSVG).
		Content(
			newBuiltWithGoapp().ID("services"),
		)
}
