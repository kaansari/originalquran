package main

import (
	"io/ioutil"
	"log"
	"path/filepath"

	"github.com/maxence-charriere/go-app/v9/pkg/app"
	"github.com/maxence-charriere/go-app/v9/pkg/ui"
	"gopkg.in/yaml.v2"
)

type MenuItem struct {
	Title string `yaml:"title"`
	URL   string `yaml:"url"`
	Icon  string `yaml:"icon"`
}

type menu struct {
	app.Compo

	Iclass string

	appInstallable bool
	Items          []MenuItem
}

func newMenu() *menu {
	return &menu{}
}

func (m *menu) Class(v string) *menu {
	m.Iclass = app.AppendClass(m.Iclass, v)
	return m
}

func (m *menu) OnNav(ctx app.Context) {
	m.appInstallable = ctx.IsAppInstallable()
}

func (m *menu) OnAppInstallChange(ctx app.Context) {
	m.appInstallable = ctx.IsAppInstallable()
}

func (m *menu) Render() app.UI {

	linkClass := "link heading fit unselectable"

	isFocus := func(path string) string {
		if app.Window().URL().Path == path {
			return "focus"
		}
		return ""
	}

	return ui.Scroll().
		Class("menu").
		Class(m.Iclass).
		HeaderHeight(headerHeight).
		Header(
			ui.Stack().
				Class("fill").
				Middle().
				Content(
					app.Header().Body(
						app.A().
							Class("heading").
							Class("app-title").
							Href("/").
							Text("NooN Spa"),
					),
				),
		).
		Content(
			app.Nav().Body(
				app.Div().Class("separator"),

				ui.Link().
					Class(linkClass).
					Icon(homeSVG).
					Label("Home").
					Href("/").
					Class(isFocus("/")),
				ui.Link().
					Class(linkClass).
					Icon(serviceSVG).
					Label("Floor Plans").
					Href("/services").
					Class(isFocus("/services")),
				ui.Link().
					Class(linkClass).
					Icon(googleSVG).
					Label("Location").
					Href("https://maps.app.goo.gl/cbnXdVd3ceyJ9NE89").
					Class(isFocus("/search")),
				ui.Link().
					Class(linkClass).
					Icon(aboutSVG).
					Label("About Us").
					Href("/aboutus").
					Class(isFocus("/aboutus")),

				app.Div().Class("separator"),

				ui.Link().
					Class(linkClass).
					Icon(facebookSVG).
					Label("FaceBook").
					Href(facebookURL),
				ui.Link().
					Class(linkClass).
					Icon(tiktokSVG).
					Label("TikTok").
					Href(tiktokURL),
				ui.Link().
					Class(linkClass).
					Icon(instagramSVG).
					Label("Instagram").
					Href(instagramURL),

				app.Div().Class("separator"),

				app.If(m.appInstallable,
					ui.Link().
						Class(linkClass).
						Icon(downloadSVG).
						Label("Install").
						OnClick(m.installApp),
				),
				ui.Link().
					Class(linkClass).
					Icon(userLockSVG).
					Label("Privacy Policy").
					Href("/privacy-policy").
					Class(isFocus("/privacy-policy")),

				app.Div().Class("separator"),
			),
		)
}

func (m *menu) loadMenuItems() {
	yamlFile := "data/menu.yaml"
	absPath, err := filepath.Abs(yamlFile)
	if err != nil {
		log.Fatalf("error getting absolute path: %v", err)
	}

	content, err := ioutil.ReadFile(absPath)
	if err != nil {
		log.Fatalf("error reading YAML file: %v", err)
	}

	err = yaml.Unmarshal(content, &m.Items)
	if err != nil {
		log.Fatalf("error unmarshaling YAML: %v", err)
	}
}

func (m *menu) installApp(ctx app.Context, e app.Event) {
	ctx.NewAction(installApp)
}
