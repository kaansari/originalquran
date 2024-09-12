package main

import (
	"github.com/maxence-charriere/go-app/v9/pkg/app"
	"github.com/maxence-charriere/go-app/v9/pkg/ui"
)

type builtWithGoapp struct {
	app.Compo

	Iid    string
	Iclass string
}

func newBuiltWithGoapp() *builtWithGoapp {
	return &builtWithGoapp{}
}

func (b *builtWithGoapp) ID(v string) *builtWithGoapp {
	b.Iid = v
	return b
}

func (b *builtWithGoapp) Class(v string) *builtWithGoapp {
	b.Iclass = app.AppendClass(b.Iclass, v)
	return b
}

func (b *builtWithGoapp) Render() app.UI {
	return app.Div().
		Class(b.Iclass).
		Body(
			ui.Flow().
				Class("p").
				StretchItems().
				Spacing(18).
				ItemWidth(600).
				Content(

					newBuiltWithGoappItem().
						Class("fill").
						Image("/web/images/models/render26.png").
						Name("TWO STORY PLAN").
						Description("2-3 bedrooms: 2,027 SQFT"),
					newBuiltWithGoappItem().
						Class("fill").
						Image("/web/images/models/front1render.png").
						Name("THREE STORY PLAN").
						Description("3-6 bedrooms: up to 3,027 SQFT"),
				),
		)
}

type builtWithGoappItem struct {
	app.Compo

	Iclass       string
	Iimage       string
	Iname        string
	Idescription string
	Ihref        string
}

func newBuiltWithGoappItem() *builtWithGoappItem {
	return &builtWithGoappItem{}
}

func (i *builtWithGoappItem) Class(v string) *builtWithGoappItem {
	i.Iclass = app.AppendClass(i.Iclass, v)
	return i
}

func (i *builtWithGoappItem) Image(v string) *builtWithGoappItem {
	i.Iimage = v
	return i
}

func (i *builtWithGoappItem) Name(v string) *builtWithGoappItem {
	i.Iname = v
	return i
}

func (i *builtWithGoappItem) Description(v string) *builtWithGoappItem {
	i.Idescription = v
	return i
}

func (i *builtWithGoappItem) Href(v string) *builtWithGoappItem {
	i.Ihref = v
	return i
}

func (i *builtWithGoappItem) Render() app.UI {
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
