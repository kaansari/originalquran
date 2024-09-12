
//starting


package main

import (
	"github.com/maxence-charriere/go-app/v9/pkg/app"
	"github.com/maxence-charriere/go-app/v9/pkg/ui"
)

type builtteamGoapp struct {
	app.Compo

	Iid    string
	Iclass string
}

func newBuiltteamGoapp() *builtteamGoapp {
	return &builtteamGoapp{}
}

func (b *builtteamGoapp) ID(v string) *builtteamGoapp {
	b.Iid = v
	return b
}

func (b *builtteamGoapp) Class(v string) *builtteamGoapp {
	b.Iclass = app.AppendClass(b.Iclass, v)
	return b
}

func (b *builtteamGoapp) Render() app.UI {
	return app.Div().
		Class(b.Iclass).
		Body(
			app.H2().
				ID(b.Iid).
				Text("MEET OUR TEAM"),
			ui.Flow().
				Class("p").
				StretchItems().
				Spacing(18).
				ItemWidth(360).
				Content(
					newBuiltteamGoappItem().
						Class("fill").
						Image("web/images/bilal.png").
						Name("Bellal Sheikh").
						Description("Physician").
						Href("ourteam"),
					newBuiltteamGoappItem().
						Class("fill").
						Image("/web/images/bri.png").
						Name("Bri Schaefer").
						Description("Nurse Injector").
						Href("ourteam"),
					newBuiltteamGoappItem().
						Class("fill").
						Image("/web/images/mary.png").
						Name("Mary Burhani").
						Description("Aesthetician").
						Href("ourteam"),
					
				),
		)
}

type builtteamGoappItem struct {
	app.Compo

	Iclass       string
	Iimage       string
	Iname        string
	Idescription string
	Ihref        string
}

func newBuiltteamGoappItem() *builtteamGoappItem {
	return &builtteamGoappItem{}
}

func (i *builtteamGoappItem) Class(v string) *builtteamGoappItem {
	i.Iclass = app.AppendClass(i.Iclass, v)
	return i
}

func (i *builtteamGoappItem) Image(v string) *builtteamGoappItem {
	i.Iimage = v
	return i
}

func (i *builtteamGoappItem) Name(v string) *builtteamGoappItem {
	i.Iname = v
	return i
}

func (i *builtteamGoappItem) Description(v string) *builtteamGoappItem {
	i.Idescription = v
	return i
}

func (i *builtteamGoappItem) Href(v string) *builtteamGoappItem {
	i.Ihref = v
	return i
}

func (i *builtteamGoappItem) Render() app.UI {
	return app.A().
		Class(i.Iclass).
		Class("block").
		Class("rounded").
		Class("text-center").
		Class("magnify").
		Class("default").
		Href(i.Ihref).
		Body(
			ui.Block().
				Class("fill").
				Middle().
				Content(
					app.Img().
						Class("hstretch").
						Alt(i.Iname+" tumbnail.").
						Src(i.Iimage),
					app.H3().Text(i.Iname),
					app.Div().
						Class("text-tiny-top").
						Text(i.Idescription),
				),
		)
}
