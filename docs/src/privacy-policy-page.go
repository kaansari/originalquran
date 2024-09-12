package main

import (
	"github.com/maxence-charriere/go-app/v9/pkg/analytics"
	"github.com/maxence-charriere/go-app/v9/pkg/app"
)

type privacyPolicyPage struct {
	app.Compo
}

func newPrivacyPolicyPage() *privacyPolicyPage {
	return &privacyPolicyPage{}
}

func (p *privacyPolicyPage) OnPreRender(ctx app.Context) {
	p.initPage(ctx)
}

func (p *privacyPolicyPage) OnNav(ctx app.Context) {
	p.initPage(ctx)
}

func (p *privacyPolicyPage) initPage(ctx app.Context) {
	ctx.Page().SetTitle("Privacy Policy")
	ctx.Page().SetDescription("go-app documentation privacy policy.")
	analytics.Page("privacy-policy", nil)
}

func (p *privacyPolicyPage) Render() app.UI {
	return newPage().
		Title("Privacy Policy").
		Icon(userLockSVG).
		Content(
			newRemoteMarkdownDoc().Src("/web/documents/privacy-policy.md"),
		)
}
