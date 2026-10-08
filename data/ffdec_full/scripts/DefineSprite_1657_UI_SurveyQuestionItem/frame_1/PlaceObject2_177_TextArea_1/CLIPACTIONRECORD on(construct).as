on(construct){
   while(true)
   {
      if(!(0x04A3DC10 & 0x04A3DC10))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x03");
      }
      if(ord(§§pop()))
      {
         while(true)
         {
            if(!(getTimer() + 1))
            {
               §§push(getProperty(§§pop(), _X));
               break;
            }
            while(true)
            {
               set("\x16\b\x02",false);
               border = false;
               set("\x17\f\x06",false);
               enabled = true;
               §§push("html");
               §§push(true);
               if(!getTimer())
               {
                  break;
               }
               set(§§pop(),§§pop());
               maxChars = -1;
               restrict = "none";
               set("\x1a\x11\x13",0);
               set("\x1a\x11\x14",true);
               selectable = false;
               §§push("styleName");
               §§push("GuildInformationsTextArea");
               if(false)
               {
                  continue;
               }
               §§push(getProperty(§§pop(), _X));
            }
            §§pop()[§§pop()] = §§pop();
         }
         §§goto(addr20cf9);
      }
      set(§§pop(),§§pop());
      §§push(§§constant(13));
      §§push(§§constant(14));
      break;
   }
   set(§§pop(),§§pop());
   set("\b\x06\b\x07\x1d{invalid_utf8=150}\x07","\b\b\x01");
   set("","\b\x05\x07{invalid_utf8=255}{invalid_utf8=255}{invalid_utf8=255}{invalid_utf8=255}\x1d{invalid_utf8=150}\x04");
   set("",true);
   addr20cf9:
}
