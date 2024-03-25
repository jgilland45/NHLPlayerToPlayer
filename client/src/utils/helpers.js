export const getHeadshotFromUrl = (imgUrl) => {
    console.log(imgUrl)
    if (imgUrl) {
        let loadImg = false
        const img = new Image()
        img.src = imgUrl
        img.onload = () => {
            loadImg = true
            console.log('loadImg: ', loadImg)
            console.log('image loaded')
        }
        img.onerror = () => {
            loadImg = false
            console.log('loadImg: ', loadImg)
            console.log('image errored')
        }
        console.log('final loadImg: ', loadImg)
        const newImgUrl = loadImg ? imgUrl : 'https://assets.nhle.com/mugs/nhl/default-skater.png'
        console.log(newImgUrl)
        return newImgUrl
    }
    return 'https://assets.nhle.com/mugs/nhl/default-skater.png'
}
