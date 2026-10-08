on(construct){
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
         §§push("\x02");
      }
      if(ord(§§pop()))
      {
         enabled = true;
         html = false;
         multiline = false;
         styleName = "BrownLeftMediumBoldLabel";
         §§push("text");
         §§push("");
         if(!getTimer())
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr91df3);
         }
      }
      set(§§pop(),§§pop());
      §§push("wordWrap");
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   addr91df3:
}
