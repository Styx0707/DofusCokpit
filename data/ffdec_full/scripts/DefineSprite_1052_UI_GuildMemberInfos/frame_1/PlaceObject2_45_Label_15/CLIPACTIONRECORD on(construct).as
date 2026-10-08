on(construct){
   while(true)
   {
      if(!ord("\x07"))
      {
         if(!ord("\x07"))
         {
            break;
         }
      }
      else
      {
         §§push("\x03");
      }
      if(!ord(§§pop()))
      {
         §§goto(addr175ce);
      }
      §§push("enabled");
      §§push(true);
      break;
   }
   set(§§pop(),§§pop());
   html = false;
   multiline = false;
   styleName = "BrownRightMediumBoldLabel";
   text = "";
   §§push("wordWrap");
   §§push(false);
   if(!ord("\x03"))
   {
      §§push(getProperty(§§pop(), _X));
   }
   else
   {
      addr175ce:
      set(§§pop(),§§pop());
      §§goto(addr17652);
   }
   addr17652:
}
