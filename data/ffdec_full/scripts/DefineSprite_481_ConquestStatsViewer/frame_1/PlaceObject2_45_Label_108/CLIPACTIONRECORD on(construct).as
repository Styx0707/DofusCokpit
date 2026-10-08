on(construct){
   while(true)
   {
      if(false)
      {
         if(!ord("\b"))
         {
            break;
         }
      }
      else
      {
         §§push("\x06");
      }
      if(ord(§§pop()))
      {
         enabled = true;
         html = false;
         multiline = false;
         styleName = "BrownCenterMediumBoldLabel";
         §§push("text");
         §§push("");
         if(!ord("\x0b"))
         {
            §§goto(addr32069);
         }
      }
      set(§§pop(),§§pop());
      §§push("wordWrap");
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   addr32069:
   getProperty(§§pop(), _X);
}
