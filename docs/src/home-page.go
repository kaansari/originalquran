package main

import (
	"github.com/maxence-charriere/go-app/v9/pkg/analytics"
	"github.com/maxence-charriere/go-app/v9/pkg/app"
	"github.com/maxence-charriere/go-app/v9/pkg/ui"
)

type homePage struct {
	app.Compo
}

func newHomePage() *homePage {
	return &homePage{}
}

func (p *homePage) OnPreRender(ctx app.Context) {
	p.initPage(ctx)
}

func (p *homePage) OnNav(ctx app.Context) {
	p.initPage(ctx)
}

func (p *homePage) initPage(ctx app.Context) {
	ctx.Page().SetTitle(defaultTitle)
	ctx.Page().SetDescription(defaultDescription)
	analytics.Page("home", nil)
}

func (p *homePage) Render() app.UI {
	return newPage().
		Title("CROSSINGS AT GREENVILLE").
		Icon(homeSVG).
		Content(
			ui.Flow().
				StretchItems().
				Spacing(84).
				Content(
					newRemoteMarkdownDoc().
						Class("fill").
						Src("/web/documents/homepage.md"),
				),
			ui.Flow().
				StretchItems().
				Spacing(84).
				Class("fill").
				Content(
					app.Raw(`
					<div>
					<svg
					aria-label="Description of the SVG content"
					   viewBox="0 0 310.90125 177.12616"
					   version="1.1"
					   id="greenvillesite"
					   xmlns:xlink="http://www.w3.org/1999/xlink"
					   xmlns="http://www.w3.org/2000/svg"
					   xmlns:svg="http://www.w3.org/2000/svg">
					  <g
						 id="site"
						 transform="matrix(1.1312292,-0.00607452,0.00748194,1.1195146,-5.6984238,-41.378279)"
						 style="display:inline;fill:#ac9d93;stroke:#000000;stroke-opacity:1">

					  </g>
					  
					  <g
						 inkscape:groupmode="layer"
						 id="layer4"
						 inkscape:label="Buildings"
						 transform="translate(-5.7954118,-24.800442)"
						 style="display:inline">
						<g
						   id="road"
						   style="display:inline;fill:#ac9d93"
						   transform="matrix(1.1488039,-0.00614983,0.00759818,1.1333938,-29.299915,-0.65031404)">
						  <path
							 d="M 0,0 V 1.2 2.28 L -0.36,3.36 -0.84,4.32 -1.56,5.16 -2.4,5.88 -3.36,6.48 -4.44,6.84 -5.52,6.96 H -6.6 L -7.68,6.72 -8.76,6.24 -9.6,5.52 -10.32,4.8 -10.92,3.84 -11.4,2.76 -11.64,1.68 V 0.6 l 0.24,-1.08 0.48,-1.08 0.6,-0.96 0.72,-0.72 0.84,-0.72 1.08,-0.36 1.08,-0.36 h 1.08 l 1.08,0.12 1.08,0.36 0.96,0.6 0.84,0.72 0.72,0.84 0.48,0.96 z m 377.04,35.82 c 0,3.21 -2.6,5.82 -5.82,5.82 -3.21,0 -5.82,-2.61 -5.82,-5.82 0,-3.21 2.61,-5.82 5.82,-5.82 3.22,0 5.82,2.61 5.82,5.82 m 87.67,145.81 0.29,-0.19 0.36,-0.36 0.36,-0.48 0.12,-0.48 0.12,-0.48 v -0.48 l -0.12,-0.48 -0.12,-0.48 -0.36,-0.48 -0.36,-0.36 -0.36,-0.36 -0.48,-0.12 -0.48,-0.24 h -0.48 -9.48 v -6.24 -6.12 -6.24 -6.12 h 10.81 c 0.84,-0.24 1.52,-0.9 1.79,-1.78 0.3,-0.96 0.04,-1.98 -0.64,-2.68 l 0.04,0.02 2.4,1.92 2.04,2.28 1.68,2.52 1.32,2.88 0.84,2.88 0.36,3.12 v 3 l -0.6,3 -0.84,2.88 -1.44,2.76 -1.8,2.52 -2.04,2.28 -2.4,1.8 z m -11.11,2.81 -10.08,0.12 -16.56,0.04 v 0.31 l -15.12,0.06 v -0.33 l -17.04,0.04 -2.4,-0.24 -2.28,-0.6 -2.04,-0.96 -0.84,-0.58 -1.08,-0.74 -1.68,-1.68 -0.72,-1.05 -0.6,-0.87 -0.96,-2.04 -0.6,-2.28 -0.24,-2.28 v -29.04 l 0.24,-2.28 0.6,-2.28 0.96,-2.04 0.6,-0.87 0.72,-1.05 1.68,-1.68 1.92,-1.32 2.04,-0.96 2.28,-0.72 2.4,-0.12 h 32.16 l 2.16,0.12 2.04,0.6 2.04,0.84 31.68,16.68 0.36,0.24 0.36,0.36 0.24,0.36 0.12,0.36 0.12,0.48 v 0.48 l -0.12,0.36 -0.24,0.48 -0.24,0.36 -0.24,0.36 -0.36,0.24 -0.48,0.12 -0.36,0.12 h -0.48 -10.2 V 177 h 9.84 0.48 l 0.36,0.12 0.48,0.24 0.36,0.24 0.24,0.36 0.24,0.36 0.12,0.36 0.12,0.48 v 0.48 l -0.12,0.36 -0.12,0.48 -0.24,0.36 -0.24,0.36 -0.36,0.24 -2.52,1.32 -2.76,0.96 -2.76,0.6 z M 347.52,61.78 l 1.32,0.14 2.4,0.6 2.16,0.96 0.79,0.59 0.06,0.04 c 0.74,0.5 1.44,1.07 2.09,1.71 0.81,0.81 1.5,1.7 2.07,2.66 l 0.03,0.04 0.03,0.07 0.93,2.09 0.6,2.4 0.24,2.4 v 6.48 0.36 6.12 6.24 6.12 6.24 0.36 27.48 0.24 6.24 6.12 6.24 6.12 6.24 0.36 5.16 l -0.24,2.4 -0.6,2.28 -0.96,2.16 -1.44,1.92 -1.68,1.68 -1.92,1.44 -2.16,0.96 -2.4,0.6 -1.32,0.14 -0.96,0.1 -2.4,0.01 -22.68,0.1 -15.12,0.06 -15.12,0.07 -15.12,0.07 -21.96,0.09 h -0.36 l -6.12,0.03 -6.24,0.03 h -0.36 l -21.96,0.09 -30.24,0.13 -15.12,0.07 -21.96,0.09 -0.36,0.01 -6.12,0.02 -6.24,0.03 h -0.36 l -21.96,0.1 -15.12,0.06 -32.04,0.14 -2.4,-0.12 -2.36,-0.59 -0.04,-0.01 -0.05,-0.02 c -3,-1.12 -5.55,-3.27 -7.15,-6.1 -0.34,-0.59 -0.63,-1.21 -0.88,-1.86 l -0.2,-0.42 -3.49,-9.84 -0.13,-0.35 -2.08,-5.87 -2.05,-5.76 -2.09,-5.9 -4.13,-11.62 -4.14,-11.66 H 38.4 L 36.36,120.6 31.85,107.87 22.44,81.36 22.17,80.33 21.84,79.08 21.8,78.34 C 21.74,77.8 21.72,77.26 21.72,76.73 v -0.05 -0.04 c 0.02,-1.39 0.26,-2.78 0.71,-4.1 l 0.13,-0.54 0.96,-2.16 1.44,-1.92 1.68,-1.68 1.1,-0.75 0.82,-0.57 2.16,-1.08 2.28,-0.6 1.38,-0.07 c 0.28,-0.03 0.57,-0.04 0.86,-0.04 l 0.16,-0.01 h 0.06 l 20.58,-0.1 15.12,-0.07 15.12,-0.07 15.12,-0.07 15,-0.06 22.08,-0.11 h 0.24 l 6.24,-0.03 6.12,-0.03 h 0.36 l 21.96,-0.1 15.12,-0.07 15.12,-0.07 15.12,-0.07 22.08,-0.1 h 0.24 l 6.24,-0.03 6.12,-0.03 h 0.36 l 21.96,-0.1 15.12,-0.07 15.12,-0.07 15.12,-0.07 23.04,-0.11 2.4,-0.01 z m 3.24,142.41 c 3.74,2.44 6.22,6.65 6.24,11.45 v 0.06 l 0.12,36.18 v 0.06 c 0,2.91 -0.6,5.68 -1.7,8.19 l 21.26,-0.09 7.9,-0.1 -0.22,-44.57 h 0.12 c 0.07,-4.77 2.47,-8.98 6.12,-11.54 1.1,-0.77 2.3,-1.38 3.6,-1.83 1.3,-0.44 2.69,-0.7 4.14,-0.75 v -0.13 h 25.38 15.12 18.96 l 3.96,-0.72 3.84,-0.96 3.6,-1.56 3.48,-1.8 3.36,-2.16 3,-2.52 2.76,-2.88 2.4,-3.12 2.16,-3.36 1.68,-3.6 1.32,-3.72 0.96,-3.84 0.48,-3.84 v -7.68 -0.06 -0.06 c -0.01,-5.52 -1.53,-10.82 -4.26,-15.4 -0.01,-0.01 -0.02,-0.03 -0.02,-0.04 -2.8,-4.68 -6.87,-8.59 -11.87,-11.22 l -0.05,-0.1 -32.04,-16.8 -3.36,-1.56 -2.65,-0.82 -0.83,-0.26 -3.6,-0.6 -2.64,-0.18 -0.96,-0.06 h -5.28 -6.12 -6.24 -6.12 -6.24 -0.36 -3.3 -0.06 c -2.85,-0.01 -5.49,-0.89 -7.68,-2.39 -1.3,-0.88 -2.44,-1.99 -3.36,-3.26 -1.66,-2.27 -2.64,-5.06 -2.64,-8.09 H 381 V 98.4 62.22 h 0.12 c 0,-2.93 0.94,-5.76 2.64,-8.08 0.34,-0.48 0.72,-0.94 1.14,-1.37 0.34,-0.37 0.71,-0.71 1.09,-1.04 L 386,51.7 c 0.76,-0.71 1.46,-1.47 2.1,-2.27 0.07,-0.08 0.14,-0.17 0.21,-0.26 1.23,-1.58 2.21,-3.3 2.95,-5.11 0.79,-1.93 1.29,-3.95 1.5,-6.01 0.22,-2.08 0.14,-4.19 -0.26,-6.27 -0.38,-2.01 -1.04,-3.98 -2.01,-5.87 -0.05,-0.11 -0.11,-0.23 -0.17,-0.34 -0.93,-1.75 -2.08,-3.33 -3.4,-4.72 -1.43,-1.52 -3.06,-2.8 -4.83,-3.83 -1.79,-1.05 -3.73,-1.84 -5.75,-2.33 -1.98,-0.5 -4.05,-0.72 -6.14,-0.63 -1.32,0.05 -2.65,0.23 -3.98,0.53 -0.75,0.17 -1.48,0.38 -2.19,0.63 -1.99,0.68 -3.85,1.64 -5.52,2.83 -1.71,1.21 -3.23,2.66 -4.51,4.3 -1.3,1.65 -2.36,3.48 -3.13,5.44 -0.75,1.87 -1.24,3.86 -1.44,5.93 -0.02,0.12 -0.03,0.24 -0.04,0.36 -0.02,0.31 -0.04,0.61 -0.05,0.92 l 0.03,0.01 c -0.22,0.85 -0.51,1.67 -0.88,2.44 -2.21,4.68 -6.95,7.78 -12.28,7.79 h -0.09 l -20.76,0.12 -5.76,0.03 -15.12,0.06 -15.12,0.07 -15.12,0.07 -21.96,0.1 h -0.36 l -6.24,0.03 -6.48,0.02 -21.96,0.1 -15.12,0.07 -15.12,0.07 -15.12,0.07 -21.96,0.09 -0.36,0.01 -6.12,0.02 -6.6,0.03 -21.96,0.1 -15.12,0.07 -15.12,0.07 -15.12,0.06 -15,0.07 -24.59,0.11 H 19.92 C 17.46,46.69 15.1,46.06 13.05,44.9 10.22,43.33 7.96,40.78 6.77,37.61 L 6.84,37.56 4.8,31.68 4.84,31.67 C 3.22,26.55 4.75,20.94 8.75,17.33 l 0.03,0.04 c 5.56,-5 8.03,-12.35 6.93,-19.43 -0.02,-0.11 -0.04,-0.23 -0.06,-0.35 -0.33,-1.92 -0.92,-3.83 -1.8,-5.65 -0.13,-0.28 -0.27,-0.56 -0.42,-0.84 -0.84,-1.58 -1.85,-3.02 -2.99,-4.3 -1.39,-1.54 -2.97,-2.86 -4.7,-3.93 -1.78,-1.11 -3.72,-1.95 -5.75,-2.51 -3.49,-0.95 -7.24,-1.04 -10.93,-0.12 -4.93,1.23 -9.11,4.1 -12.02,7.94 -1.31,1.73 -2.37,3.66 -3.11,5.73 -0.69,1.89 -1.12,3.9 -1.24,5.97 -0.01,0.12 -0.02,0.24 -0.02,0.36 -0.02,0.32 -0.03,0.63 -0.03,0.95 h -0.02 c -0.05,0.92 -0.19,1.82 -0.42,2.69 -0.36,1.43 -0.95,2.77 -1.74,3.99 -1.6,2.52 -4.01,4.51 -6.94,5.57 h -0.12 l -39.6,14.04 0.06,0.19 c -3.11,1.09 -6.36,0.99 -9.24,-0.05 -3.72,-1.35 -6.83,-4.3 -8.26,-8.32 l 20.56,57.86 -0.72,-2.76 -0.36,-2.88 0.12,-2.88 0.48,-2.88 0.84,-2.88 0.48,-0.96 0.84,-1.68 1.56,-2.4 0.66,-0.74 1.26,-1.42 2.28,-1.8 2.52,-1.56 2.64,-1.2 35.64,-12.6 0.02,-0.05 c 2.89,-1.03 5.89,-1.03 8.62,-0.19 1.51,0.46 2.94,1.18 4.22,2.14 2.09,1.56 3.76,3.73 4.7,6.37 l -0.04,0.01 6.48,18.24 5.07,14.27 5.03,14.16 5.07,14.27 14.72,41.42 5.07,14.27 5.03,14.16 9.09,25.57 19.68,-0.09 15.12,-0.07 15.12,-0.07 15.12,-0.07 21.96,-0.1 0.36,-0.01 6.24,-0.02 6.12,-0.03 h 0.36 l 21.96,-0.11 15.12,-0.07 15.12,-0.07 15.12,-0.07 22.32,-0.1 6.12,-0.03 6.24,-0.03 h 0.36 l 21.96,-0.1 15.12,-0.07 15.12,-0.07 15.12,-0.07 14.88,-0.07 h 10.32 l 0.06,0.12 c 1.4,0 2.75,0.21 4.02,0.6 1.25,0.38 2.42,0.93 3.48,1.63"
							 style="display:inline;fill:#999999;fill-opacity:1;fill-rule:nonzero;stroke:none"
							 transform="matrix(0.35277776,0,0,-0.35277776,76.514841,143.04203)"
							 clip-path="url(#clipPath868)"
							 id="path929" />
						</g>
						<g
						   id="c5-9"
						   transform="matrix(0.15691652,-0.44545738,0.50391129,0.17750745,2.8059133,162.80558)"
						   style="fill:#0000ff">
						  <rect
							 id="c5"
							 width="12"
							 height="32"
							 x="142"
							 y="48"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="c6"
							 width="12"
							 height="32"
							 x="129"
							 y="48"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="c7"
							 width="12"
							 height="32"
							 x="116"
							 y="48"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="c8"
							 width="12"
							 height="32"
							 x="103"
							 y="48"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="c9"
							 width="12"
							 height="32"
							 x="90"
							 y="48"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="c1-4"
						   transform="matrix(0.15974989,-0.44444915,0.50277075,0.18071262,14.405578,129.44918)"
						   style="fill:#0000ff">
						  <rect
							 id="c1"
							 width="12"
							 height="32"
							 x="129"
							 y="48"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="c2"
							 width="12"
							 height="32"
							 x="116"
							 y="48"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="c3"
							 width="12"
							 height="32"
							 x="103"
							 y="48"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="c4"
							 width="12"
							 height="32"
							 x="90"
							 y="48"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="g1"
						   transform="matrix(0.47228707,0,0,0.53426162,95.268023,49.843787)"
						   style="fill:#808080">
						  <rect
							 id="d1"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="d2"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="d3"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="d4"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="d5"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="g1-5"
						   transform="matrix(0.47228707,0,0,0.53426162,95.306659,79.168642)"
						   style="fill:#808080">
						  <rect
							 id="G1"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G2"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G3"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G4"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G5"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="h1-5"
						   transform="matrix(0.47228707,0,0,0.53426162,95.294451,105.92818)"
						   style="fill:#808080">
						  <rect
							 id="H1"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H2"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H3"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H4"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H5"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="g11-16"
						   transform="matrix(0.47228707,0,0,0.53426162,13.589209,79.576255)"
						   style="fill:#808080">
						  <rect
							 id="G11"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G12"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G13"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G14"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G15"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G16"
							 width="12"
							 height="32"
							 x="142"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="h11-16"
						   transform="matrix(0.47228707,0,0,0.53426162,7.8018926,105.87111)"
						   style="fill:#808080">
						  <rect
							 id="H11"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H12"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H13"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H14"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H15"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H16"
							 width="12"
							 height="32"
							 x="142"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="e3-1"
						   transform="matrix(0.47228707,0,0,0.53426162,137.69314,49.447736)"
						   style="fill:#808080">
						  <rect
							 id="E3"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="E32"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="E1"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="a1-5"
						   transform="matrix(0.00374408,-0.47227223,0.53424483,0.00423539,220.74867,179.24526)"
						   >
						  <rect
							 id="F1"
							 width="12"
							 height="32"
							 x="193"
							 y="70"
							 style="fill:#ff0000" stroke="#c78d84" stroke-width="0.75"/>
						  <rect
							 id="F2"
							 width="12"
							 height="32"
							 x="180"
							 y="70"
							 style="fill:#ff0000" stroke="#c78d84" stroke-width="0.75" />
						</g>
						<g
						   id="g6-10"
						   transform="matrix(0.47228707,0,0,0.53426162,53.414723,79.197449)"
						   style="fill:#808080">
						  <rect
							 id="G6"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G7"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G8"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G9"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="G10"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="d6-10"
						   transform="matrix(0.47228707,0,0,0.53426162,53.513135,49.80273)"
						   style="fill:#808080">
						  <rect
							 id="D6"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="D7"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="D8"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="D9"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="D10"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="d11-13"
						   transform="matrix(0.47228707,0,0,0.53426162,11.457087,49.57476)"
						   style="fill:#808080">
						  <rect
							 id="D11"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="D12"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="D13"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="a6-10"
						   transform="matrix(0.47228707,0,0,0.53426162,53.344624,24.048037)"
						   style="fill:#808080">
						  <rect
							 id="A6"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A7"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A8"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A9"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A10"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="g12"
						   transform="matrix(0.47228707,0,0,0.53426162,95.244364,24.054281)"
						   style="fill:#808080">
						  <rect
							 id="A1"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A2"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A3"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A4"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A5"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<g
						   id="b1-5"
						   transform="matrix(0.47228707,0,0,0.53426162,149.34202,24.357112)"
						   style="fill:#ff0000">
						  <rect
							 id="B1"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 style="fill:#ff0000" />
						  <rect
							 id="B2"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 style="fill:#ff0000" />
						  <rect
							 id="B3"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 style="fill:#ff0000" />
						  <rect
							 id="B4"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 style="fill:#ff0000" />
						  <rect
							 id="B5"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 style="fill:#ff0000" />
						</g>
						<g
						   id="a11-15"
						   transform="matrix(0.47228707,0,0,0.53426162,11.443606,24.294457)"
						   style="fill:#808080">
						  <rect
							 id="A11"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A12"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A13"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A14"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="A15"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						</g>
						<a href="/privacy-policy">
						<g
						   id="h6-10"
						   transform="matrix(0.47228707,0,0,0.53426162,53.391092,106.05071)"
						   style="fill:#808080">
						  <rect
							 id="H6"
							 width="12"
							 height="32"
							 x="207"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H7"
							 width="12"
							 height="32"
							 x="194"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H8"
							 width="12"
							 height="32"
							 x="181"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
						  <rect
							 id="H9"
							 width="12"
							 height="32"
							 x="168"
							 y="70"
							 fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75" />
							
						 <rect 
						  description="3 Bedroom" class="enabled" fill="#E0E0E0" stroke="#FFFFFF" stroke-width="0.75"
							 id="H10"
							 width="12"
							 height="32"
							 x="155"
							 y="70"
							 />
						</g>
						</a>
					  </g>
					  <g
						 inkscape:groupmode="layer"
						 id="layer5"
						 style="display:inline"
						 transform="translate(169.22307,-28.574768)">
						<text
						   x="155"
						   y="70"
						   font-size="4px"
						   fill="#ffffff"
						   text-anchor="middle"
						   alignment-baseline="middle"
						   transform="rotate(90,100,20)"
						   id="text1">SOLD</text>
					  </g>
					</svg>
					<div class="description"/>
					</div>
					`),

					app.Script().
						Src("/web/js/svgscript.js").Async(true),
				),

			app.H2().Text("Plans"),

			newBuiltWithGoapp().ID("built-with-go-app"),

			app.Div().Class("separator"),

			newRemoteMarkdownDoc().Src("/web/documents/home-next.md"),
		)

}
