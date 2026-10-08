on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!(0x115B3135 | 0x115B3135))
         {
            if(false)
            {
               while(true)
               {
                  set("\x02","\x1a");
                  set("{invalid_utf8=200}\x19",0);
                  set("\x1d{invalid_utf8=150}\x04",true);
                  set("\b\x06\b\x07\x1d{invalid_utf8=150}\x07",false);
                  §§push("\b\b\x01");
                  §§push("");
                  if(!getTimer())
                  {
                     duplicateMovieClip(§§pop(),§§pop(),§§pop());
                     §§goto(addr199a1);
                  }
                  §§goto(addr19a71);
                  break loop3;
               }
               §§goto(addr19a70);
               addr19970:
            }
         }
         else
         {
            §§push("\b");
         }
         if(!ord(§§pop()))
         {
            break;
         }
         break loop2;
      }
      set(§§pop(),§§pop());
      §§goto(addr19970);
   }
   while(true)
   {
      set("{invalid_utf8=150}\x03",false);
      set("",false);
      set("\b",false);
      set("2{invalid_utf8=157}\x02",true);
      v = true;
      §§push("{invalid_utf8=136}\x07");
      §§push(-1);
      if(getTimer() + 1)
      {
         break loop3;
      }
      §§pop() implements ;
      §§goto(addr199db);
      addr199db:
   }
   break loop3;
   addr199a1:
   addr19a71:
   set(§§pop(),new §\§\§pop()§());
   styleSheet = "";
   text = "";
   url = "";
   wordWrap = true;
   addr19a70:
}
