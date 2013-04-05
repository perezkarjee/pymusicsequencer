import os
import StringIO
import pymedia
import threading
import logging
import time

# Audio options
WAV = {
       "bytes_minimum":4096,
       }

MP3 = {
       "bytes_minimum":4096*2,
       }

OGG = {
       "bytes_minimum":4096*4,
       }


FORMATS = {
           ".wav":WAV,
           ".mp3":MP3,
           ".ogg":OGG,
           }

__doc__ = """This library contains the Player class which is the threaded player for music/sfx playback with the backing of pymedia library."""

class Player(threading.Thread):
    '''Simple media player written with threaded support based on pymedia.

    This threaded player will attempt to retrieve data from any kind of file object with seek 
    and read method. It will then, based on the passed filename, decide which codec to use and 
    demux + decode the data on the fly. It will require the constant FORMATS 
    to be declared, with the number of bytes per tick to read. 
    
    Player can be played, paused or stopped. However, the change will only manifest 
    itself when the tick passed (ie enough data was processed). This is FORMATS based 
    because different formats need different minimal data volume per block to success
    fully demux and decode.
    
    '''

    def __init__(self):
        '''Constructor'''
        threading.Thread.__init__(self)
        
        self.alive = True
        self.dec = None
        self.volume = 1.0
        self.repeat = True
        self.data = None
        self.finfoformat = None
        self.audioobj = None
        self.mplay = False
        
        def null():
             pass  # empty call in case we do not need the exception_call
        
        self.exception_call = null
        
    
    def set_exception_callback(self, what):
        self.exception_call = what
        
        
    def __set_volume(self):
        """Internal volume setter.

        This method it called every tick to set the volume.
        """
        volume = int(100 * self.volume)
        vol = (volume << 8) + volume
        if vol > ((100 << 8) + 100):
            vol = (100 << 8) + 100
        elif vol < 0:
            vol = 0
        self.audioobj.setVolume(vol)   
    
    
    def get_volume(self):
        """returns the volume.
        
        Returns:
            
            volume    -    0xFFFF formated volume (100 is max).
            
        This volume is the volume of the sound mixer, not the track itself!
        """
        volume = self.audioobj.getVolume()
        return volume
        
    
    def is_alive(self):
        """returns the thread status."""
        return self.alive
    
    
    def change_repeat(self, repeatval):
        """changes the repeat of the music/sound playback.

        Parameters:
            
            repeatval    -    Boolean
        """
        self.repeat = repeatval
        
    
    def add_data(self, io, ext="foo.wav"):
        """loads the demuxer and Input/Output object.

        Parameters:
        
            io    -    File like object, with seek and read methods
        
        Optional parameters:
            
            ext    -    File name containing extension, used for initializing demuxer.
        """
        self.finfoformat = FORMATS[os.path.splitext(ext)[1]]
        self.dm = pymedia.muxer.Demuxer(str.split(ext,".")[-1].lower())
            
        self.data = io
        self.data.seek(0)
    
    
    def play(self):
        """starts the playback."""
        self.mplay = True
        
    
    def pause(self):
        """pauses the playback."""
        self.mplay = False
        
    
    def resume(self):
        """resumes the playback"""
        self.play()
        
    
    def stop(self):
        """suspends the playback and kills the thread."""
        self.pause()
        self.kill()
        
        
    def kill(self):
        """kills the thread."""
        self.alive = False
    
    
    def run(self):
        """main thread instance loop.

        This loop operates in ticks, with one tick being one round of the loop. 
        The loop starts with loading the data from the IO source into the buffer 
        then if the data is less than the full amount, it will either decide to 
        reload the buffer or to kill the playback and the loop (based on the 
        repeat value).
        
        Afterwards, it will try to demux the frames out of the loaded buffer 
        and should it succeed, it will then play all the frames it was successful 
        in the demuxing.
        
        The volume setter is set every time the frame is being played, so the fadeout 
        should be working on the system that is supporting it (not supporting systems 
        include PulseAudio or Alsa, but Windows seems to work). 
        
        In this part of the loop, the audio playback device is instantiated, and should 
        it fail with SoundError exception, it will be logged and thread will be promptly
        killed with a return. The callback exception will be called as well.
        
        If no problems were detected, the playback will continue until the whole IO object 
        was used and either loop or end.
        """
        buf = ""
        while self.alive:
            if self.mplay:
                buf += self.data.read(self.finfoformat["bytes_minimum"])
                if len(buf) < self.finfoformat["bytes_minimum"]:
                    if self.repeat:
                        self.data.seek(0)
                    else:
                        while self.audioobj.isPlaying():
                            time.sleep( 0.05 )                 
                        self.kill()
                try:
                    frames = self.dm.parse(buf)
                except:
                    frames = None
                if frames:
                    for fr in frames:
                        if not self.mplay:
                            break
                        if self.dec is None:
                            self.dec = pymedia.audio.acodec.Decoder(self.dm.streams[fr[0]])
                        dat = self.dec.decode(fr[1])
                        if dat is not None:
                            if self.audioobj is None:
                                try:
                                    self.audioobj = pymedia.audio.sound.Output(dat.sample_rate, dat.channels, pymedia.audio.sound.AFMT_S16_LE)
                                except pymedia.audio.sound.SoundError, e:
                                    logging.error("Music thread failed with: %s" %str(e))
                                    self.exception_call()
                                    return
                                
                            self.__set_volume()
                            self.audioobj.play(dat.data)
                            buf = ""

                            

"""
Usage:
# we grab the source to StringIO (doesnt have to be, but its better
not to read from the hdd all the time)
media = open("foo.mp3", "rb")
source = StringIO.StringIO(media.read())
media.close()

# we make player instance
player = Player()

# We pass the data to the player and run the thread (it will not start
the playback until we run .play() method though
player.add_data(source, "foo.mp3")
player.run()

# we set up the exception callback if we need the info that playback failed
player.set_exception_callback(my_exception_catching_func)

# we start the playback
player.play()

# we change the volume to 50%
player.volume = 0.5

# we pause player
player.pause()

# we resume player
player.resume()
or
player.play()

# we loop player
player.change_repeat(True)
or
player.repeat = True

# we end the playback
player.stop()


"""
