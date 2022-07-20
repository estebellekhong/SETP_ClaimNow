import React from 'react'
import videobg from '../assets/VideoBG.mp4'

const Main = () => {
    return (
        
        <div className='main'>
            <video src={videobg} autoPlay loop muted/>
        </div>
    )
}

export default Main