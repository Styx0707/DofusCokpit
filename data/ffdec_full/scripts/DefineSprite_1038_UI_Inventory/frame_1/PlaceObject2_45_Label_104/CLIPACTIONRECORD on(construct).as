on(construct){
   while(true)
   {
      if(!(0x2F7C7C06 | 0x2F7C7C06))
      {
         if(!ord("\t"))
         {
            break;
         }
      }
      else
      {
         §§push("\x02");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      enabled = true;
      html = false;
      multiline = false;
      styleName = "WhiteCenterMediumLabel";
      §§push("text");
      §§push("");
      if(!getTimer())
      {
         setProperty(§§pop(), _X, §§pop());
         §§goto(addr0dbd);
      }
      break;
   }
   set(§§pop(),§§pop());
   wordWrap = false;
   addr0dbd:
}
