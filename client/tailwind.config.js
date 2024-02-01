module.exports = {
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './composables/**/*.{js,ts}',
    './plugins/**/*.{js,ts}',
    './views/**/*.{vue,js,ts}',
    './stores/**/*.{vue,js,ts}',
    './App.{js,ts,vue}',
    './app.{js,ts,vue}',
    './Error.{js,ts,vue}',
    './error.{js,ts,vue}'
  ],
  theme: {
    extend: {
      screens: {
        mobile: { max: '639px' },
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1440px',
        '3xl': '1600px',
        '4xl': '1921px'
      },
      height: {
        navBar: '60px'
      },
      minWidth: {
        screen: '100vw'
      },
      minHeight: {
        screen: '100vh'
      },
      colors: {
        yellow: {
          100: '#FBE0AB',
          200: '#F9D182',
          300: '#F8BF58',
          400: '#F3A927',
          500: '#D09123',
          600: '#D69C00',
          bar: '#EAA200',
          main: '#EEB311',
          bg: '#F0C95D',
          accent: '#F2DEA7'
        },
        grey: {
          50: '#F9FAFB',
          100: '#27272A',
          300: '#323232',
          400: '#838383',
          500: '#999999',
          600: '#D9D9D9',
          axis: '#BEBEBE',
          tick: '#4D4D4D',
          slope: '#88888887',
          map: '#DFDEDE',
          mapBorder: '#9E9E9E',
          trendBorder: '#838383',
          bar: '#D6D6D6'
        },
        zinc: {
          50: '#FAFAFA',
          300: '#D4D4D8',
          400: '#A1A1AA'
        },
        blue: {
          slope: '#084EA0',
          300: '#0A4EA0',
          link: '#2472ED'
        }
      }
    },
    fontFamily: {
      body: ['Libre Franklin', 'sans-serif'],
      libre: ['Libre Franklin', 'sans-serif']
    }
  },
  plugins: []
}
