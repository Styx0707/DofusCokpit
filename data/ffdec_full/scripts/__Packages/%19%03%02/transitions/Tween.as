var _loc1_;
loop35:
while(true)
{
   if(!ord("\b"))
   {
      if(false)
      {
         break;
      }
   }
   else
   {
      §§push("\x06");
   }
   if(!ord(§§pop()))
   {
      break;
   }
   loop0:
   while(true)
   {
      while(true)
      {
         loop37:
         while(true)
         {
            if(!(getTimer() + 1))
            {
               duplicateMovieClip(§§pop(),§§pop(),§§pop());
               while(true)
               {
                  §§pop()[§§pop()] = §§pop();
                  §§push(_loc1_);
                  §§push("fforward");
                  if(false)
                  {
                     break loop37;
                  }
                  while(true)
                  {
                  }
                  function()
                  {
                     this.time = this._duration;
                     this.fixTime();
                  }
                  loop2:
                  while(true)
                  {
                     if(!(getTimer() + 1))
                     {
                        duplicateMovieClip(§§pop(),§§pop(),§§pop());
                        while(true)
                        {
                        }
                        function(finish, §\x17\n\x1b§)
                        {
                           this.begin = this.position;
                           this.finish = finish;
                           if(§\x17\n\x1b§ != undefined)
                           {
                              §§push(this);
                              §§push("duration");
                              §§push(§\x17\n\x1b§);
                              if(false)
                              {
                                 setProperty(§§pop(), _X, §§pop());
                              }
                              §§pop()[§§pop()] = §§pop();
                           }
                           this.start();
                        }
                        while(getTimer())
                        {
                           §§pop()[§§pop()] = §§pop();
                           §§push(_loc1_);
                           §§push("yoyo");
                           if(getTimer() + 1)
                           {
                              while(true)
                              {
                              }
                              function()
                              {
                                 this.continueTo(this.begin,this.time);
                              }
                              while(ord("\x06"))
                              {
                                 while(true)
                                 {
                                    §§pop()[§§pop()] = §§pop();
                                    §§push(_loc1_);
                                    §§push("startEnterFrame");
                                    while(true)
                                    {
                                    }
                                    §§push(function()
                                    {
                                       if(this._fps == undefined)
                                       {
                                          _global.MovieClip.addListener(this);
                                       }
                                       else
                                       {
                                          this._intervalID = _global.setInterval(this,"onEnterFrame",1000 / this._fps);
                                       }
                                       this.isPlaying = true;
                                    });
                                    while(!(getTimer() + 1))
                                    {
                                       §§push(getProperty(§§pop(), _X));
                                       break loop66;
                                    }
                                    §§pop()[§§pop()] = §§pop();
                                    §§push(_loc1_);
                                    §§push("stopEnterFrame");
                                    if(!(getTimer() + 1))
                                    {
                                       continue loop0;
                                    }
                                    while(true)
                                    {
                                    }
                                    function()
                                    {
                                       if(this._fps == undefined)
                                       {
                                          _global.MovieClip.removeListener(this);
                                       }
                                       else
                                       {
                                          §§push(this);
                                          §§push("_intervalID");
                                          if(false)
                                          {
                                             §§pop()[§§pop()] = §§pop();
                                          }
                                          _global.clearInterval(§§pop()[§§pop()]);
                                       }
                                       this.isPlaying = false;
                                    }
                                 }
                                 break loop35;
                              }
                              startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
                              §§pop()[§§pop()] = §§pop();
                              §§push(_loc1_);
                              §§push("rewind");
                              if(getTimer())
                              {
                                 while(true)
                                 {
                                 }
                                 function(§\x1b\r\x13§)
                                 {
                                    this._time = §\x1b\r\x13§ != undefined ? §\x1b\r\x13§ : 0;
                                    this.fixTime();
                                    this["\x1b\x14\x02"]();
                                 }
                                 while(!getTimer())
                                 {
                                    §§push(getProperty(§§pop(), _X));
                                    function()
                                    {
                                       if(!this.useSeconds)
                                       {
                                          this.time = this._time - 1;
                                       }
                                    }
                                    if(!(getTimer() + 1))
                                    {
                                       §§push(§§pop()());
                                       function()
                                       {
                                          return this._duration;
                                       }
                                       if(!(getTimer() + 1))
                                       {
                                          setProperty(§§pop(), _X, §§pop());
                                          while(true)
                                          {
                                          }
                                          function()
                                          {
                                             this.rewind();
                                             this.startEnterFrame();
                                             this.broadcastMessage("onMotionStarted",this);
                                          }
                                          while(getTimer())
                                          {
                                             while(true)
                                             {
                                                §§pop()[§§pop()] = §§pop();
                                                §§push(_loc1_);
                                                §§push("stop");
                                                if(false)
                                                {
                                                   §§push(§§pop()(§§pop()));
                                                   break loop49;
                                                }
                                                addr11586:
                                                while(true)
                                                {
                                                }
                                                function()
                                                {
                                                   this.stopEnterFrame();
                                                   this.broadcastMessage("onMotionStopped",this);
                                                }
                                                continue loop49;
                                             }
                                             break loop35;
                                          }
                                          §§pop()[§§pop()] = §§pop();
                                          while(true)
                                          {
                                          }
                                          function(§\x19\x11\x19§, §\x1a\b\x04§, func, begin, finish, §\x17\n\x1b§, useSeconds)
                                          {
                                             eval("\x19\x03\x02").transitions.OnEnterFrameBeacon["\x18\t\x0b"]();
                                             loop1:
                                             while(true)
                                             {
                                                §§push(arguments);
                                                §§push("length");
                                                if(false)
                                                {
                                                   §§push(getProperty(§§pop(), _X));
                                                   while(true)
                                                   {
                                                      §§pop()[§§pop()] = §§pop();
                                                      this.duration = §\x17\n\x1b§;
                                                      this.useSeconds = useSeconds;
                                                      if(func)
                                                      {
                                                         this.func = func;
                                                      }
                                                      this.finish = finish;
                                                      §§push(this);
                                                      §§push("_listeners");
                                                      §§push([]);
                                                      if(getTimer() + 1)
                                                      {
                                                         break loop1;
                                                      }
                                                      duplicateMovieClip(§§pop(),§§pop(),§§pop());
                                                   }
                                                   addr10bfa:
                                                   return undefined;
                                                   addr10ba9:
                                                }
                                                if(§§pop()[§§pop()])
                                                {
                                                   this.obj = §\x19\x11\x19§;
                                                   this.prop = §\x1a\b\x04§;
                                                   this.begin = begin;
                                                   §§push(this);
                                                   §§push("position");
                                                   §§push(begin);
                                                   if(ord("\x04"))
                                                   {
                                                      §§goto(addr10ba9);
                                                   }
                                                   §§push(getProperty(§§pop(), _X));
                                                   break;
                                                }
                                                §§goto(addr10bfa);
                                             }
                                             §§pop()[§§pop()] = §§pop();
                                             this.addListener(this);
                                             this.start();
                                          }
                                       }
                                       break loop49;
                                    }
                                    break loop43;
                                 }
                                 break loop2;
                                 break loop35;
                              }
                              duplicateMovieClip(§§pop(),§§pop(),§§pop());
                           }
                           startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
                           break loop54;
                        }
                        §§push(new §\§\§pop()§());
                        while(true)
                        {
                        }
                        function(§\x17\x04\x15§)
                        {
                           §§push(this);
                           §§push("_duration");
                           if(!(§\x17\x04\x15§ == null || §\x17\x04\x15§ <= 0))
                           {
                              §§push(§\x17\x04\x15§);
                           }
                           else
                           {
                              §§push(_global);
                              §§push("Infinity");
                              if(!ord("\t"))
                              {
                                 var §§pop() = §§pop();
                              }
                              §§push(§§pop()[§§pop()]);
                           }
                           §§pop()[§§pop()] = §§pop();
                           return this.duration;
                        }
                     }
                     §§pop()[§§pop()] = §§pop();
                     §§push(_loc1_);
                     §§push("nextFrame");
                     if(ord("\x03"))
                     {
                        addr10d80:
                        function()
                        {
                           if(this.useSeconds)
                           {
                              this.time = (getTimer() - this._startTime) / 1000;
                           }
                           else
                           {
                              §§push(this);
                              §§push("time");
                              §§push(this);
                              §§push("_time");
                              if(false)
                              {
                                 §§push(§§pop()(§§pop()));
                              }
                              §§pop()[§§pop()] = §§pop()[§§pop()] + 1;
                           }
                        }
                        if(getTimer() + 1)
                        {
                           while(true)
                           {
                              §§pop()[§§pop()] = §§pop();
                              §§push(_loc1_);
                              §§push("onEnterFrame");
                              if(ord("\x06"))
                              {
                                 while(true)
                                 {
                                 }
                                 function()
                                 {
                                    this.nextFrame();
                                 }
                                 while(true)
                                 {
                                    if(!ord("\b"))
                                    {
                                       §§push(getProperty(§§pop(), _X));
                                       while(true)
                                       {
                                          §§pop()[§§pop()] = §§pop();
                                          §§push(_loc1_);
                                          §§push("__set__finish");
                                          if(false)
                                          {
                                             break loop42;
                                          }
                                          function(§\x17\x0f\t§)
                                          {
                                             this.change = §\x17\x0f\t§ - this.begin;
                                             return this.finish;
                                          }
                                          continue loop45;
                                       }
                                       break loop35;
                                    }
                                    while(true)
                                    {
                                       §§pop()[§§pop()] = §§pop();
                                       §§push(_loc1_);
                                       §§push("prevFrame");
                                       if(!ord("\b"))
                                       {
                                          break loop40;
                                       }
                                       §§goto(addr10aa5);
                                    }
                                    break loop35;
                                 }
                                 break loop35;
                              }
                              var §§pop() = §§pop();
                              §§goto(addr10d80);
                           }
                           break loop35;
                        }
                        §§pop() implements ;
                        while(true)
                        {
                        }
                        function(§\x1b\r\x13§)
                        {
                           this.prevTime = this._time;
                           if(§\x1b\r\x13§ > this.duration)
                           {
                              loop0:
                              while(true)
                              {
                                 while(true)
                                 {
                                    if(this.looping)
                                    {
                                       §§push(§\x1b\r\x13§);
                                       §§push(this);
                                       §§push("_duration");
                                       if(getTimer() + 1)
                                       {
                                          addr10e7b:
                                          this.rewind(§§pop() - §§pop()[§§pop()]);
                                          this["\x1b\x14\x02"]();
                                          this.broadcastMessage("onMotionLooped",this);
                                          break;
                                       }
                                       §§push(§§pop()());
                                    }
                                    else
                                    {
                                       §§push(this);
                                       §§push("useSeconds");
                                       if(!ord("\n"))
                                       {
                                          setProperty(§§pop(), _X, §§pop());
                                       }
                                       if(§§pop()[§§pop()])
                                       {
                                          this._time = this._duration;
                                          this["\x1b\x14\x02"]();
                                       }
                                       §§push(0);
                                       §§push(this);
                                       §§push("stop");
                                       if(!(getTimer() + 1))
                                       {
                                          §§pop() implements ;
                                          addr10efa:
                                          §§pop()[§§pop()]();
                                          break loop0;
                                       }
                                    }
                                    §§pop()[§§pop()]();
                                    this.broadcastMessage("onMotionFinished",this);
                                    break;
                                 }
                                 break;
                              }
                           }
                           else
                           {
                              if(§\x1b\r\x13§ >= 0)
                              {
                                 this._time = §\x1b\r\x13§;
                                 this["\x1b\x14\x02"]();
                                 break loop0;
                              }
                              this.rewind();
                              §§push(0);
                              §§push(this);
                              §§push("\x1b\x14\x02");
                              if(!getTimer())
                              {
                                 §§pop() implements ;
                                 §§goto(addr10e7b);
                              }
                              else
                              {
                                 §§goto(addr10efa);
                              }
                           }
                           break loop0;
                        }
                        loop27:
                        while(false)
                        {
                           §§push(getProperty(§§pop(), _X));
                           while(true)
                           {
                           }
                           function()
                           {
                              return this.getPosition();
                           }
                           while(!(getTimer() + 1))
                           {
                              §§pop() implements ;
                              §§pop()[§§pop()] = §§pop();
                              _loc1_.addProperty("time",_loc1_["\x0b\x1a"],_loc1_.__set__time);
                              §§push(_loc1_);
                              §§push("__set__finish");
                              if(!getTimer())
                              {
                                 §§push(new §\§\§pop()§());
                                 while(true)
                                 {
                                    §§pop()[§§pop()] = §§pop();
                                    §§push(_loc1_);
                                    §§push("__get__FPS");
                                    if(ord("\x07"))
                                    {
                                       break loop54;
                                    }
                                    var §§pop() = §§pop();
                                    _loc1_ = §§pop()[§§pop()] = §§pop().prototype;
                                    §§push(_loc1_);
                                    §§push("__set__time");
                                    if(false)
                                    {
                                       §§pop() implements ;
                                       break loop45;
                                    }
                                    continue loop27;
                                 }
                                 break loop35;
                              }
                              break loop55;
                           }
                           break loop69;
                           break loop35;
                        }
                     }
                     §§pop()[§§pop()] = getProperty(§§pop(), _X);
                     §§push(_loc1_);
                     §§push("\x1a\x18\x1c");
                     if(!ord("\x02"))
                     {
                        break loop63;
                     }
                     function(p)
                     {
                        this.prevPos = this._pos;
                        §§push(this.obj);
                        §§push(this.prop);
                        §§push(this._pos = p);
                        if(false)
                        {
                           §§push(getProperty(§§pop(), _X));
                        }
                        §§pop()[§§pop()] = §§pop();
                        this.broadcastMessage("onMotionChanged",this,this._pos);
                        _global.updateAfterEvent();
                     }
                     if(!getTimer())
                     {
                        var §§pop() = §§pop();
                        while(true)
                        {
                           §§pop()[§§pop()].transitions = new Object();
                           while(true)
                           {
                              §§push(_global["\x19\x03\x02"].transitions);
                              §§push("Tween");
                              if(!(getTimer() + 1))
                              {
                                 §§pop() implements ;
                                 continue loop67;
                              }
                              §§goto(addr10b39);
                           }
                           break loop38;
                        }
                        break loop35;
                     }
                     continue loop38;
                     §§push(getProperty(§§pop(), _X));
                  }
               }
               break loop35;
            }
            if(eval("\x19\x03\x02").transitions.Tween)
            {
               break loop38;
            }
            §§push("\x19\x03\x02");
            if(getTimer() + 1)
            {
               break loop47;
            }
            §§push(§§pop()());
            §§goto(addr11586);
         }
         §§push(new §\§\§pop()§());
         return;
      }
      var §§pop() = §§pop();
      §§pop()[§§pop()] = §§pop();
      break;
   }
   return;
}
break loop19;
